# heuristic.py
from ability import (
    BanishItemAbility, DamageTriggeredAbility, HealingTriggeredAbility,
    DrawCardsActionAbility, HealAllCharactersAbility, 
    InkTopCardAbility, DamageAllOpponentsAbility, TargetedHealingAbility, TriggeredAbility
)
from action import MulliganAction, InkAction, PassAction, PlayCardAction, QuestAction, ChallengeAction, ChallengeTargetAction, TriggeredAbilityAction
from decklists import CharacterCard, ItemCard,ActionCard
from game_enums import GamePhase 


def mulligan_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    mulligans = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, MulliganAction)
    ]
    if not mulligans:
        return None, 0.0

    hand = gamestate.engine.currentPlayer.hand
    low_curve = sum(1 for c in hand if c.cost <= 3)

    def score(a):   return -a.card.cost

    # dig for low cost cards if you have few
    if low_curve < 2:
        # shuffle away the highest cost card
        best_idx, best_action = max(mulligans, key=lambda x: score(x[1]))
        return best_idx, score(best_action)
    return None, 0.0


def ink_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    inks = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, InkAction)
    ]
    if not inks:
        return None, 0.0
    
    player = gamestate.engine.currentPlayer
    ink_total = player.ready_ink + player.exerted_ink
    hand = player.hand
    hand_size = len(hand)

    # Questo è il costo massimo delle carte IN MANO (esclusa quella che stiamo inchiostrando)
    # Lo useremo per decidere quando smettere di inchiostrare.
    def get_max_cost_in_hand(card_to_ignore):
        return max(
            (c.cost for c in hand if c != card_to_ignore and hasattr(c, "cost")),
            default=0
        )

    # Punteggi da calibrare
    BONUS_TARGET_CARD = 30  
    BONUS_EARLY_RAMP = 15
    BONUS_MID_RAMP = 5
    
    def score(a):
        card_to_ink = a.card

        
        # Non inchiostrare l'ultima carta
        if hand_size <= 1:
            return float("-inf")
        
        # Logica "Mano da 2 carte": non inchiostrare se poi non puoi giocare l'altra.
        if hand_size == 2:
            other_card = next((c for c in hand if c != card_to_ink),None)
            new_ink_total = ink_total + 1
            
            # Se l'altra carta non ha costo o costerà comunque troppo, non inchiostrare.
            if not hasattr(other_card, 'cost') or other_card.cost > new_ink_total:
                return float("-inf")
        
        # Logica "Late Game": Smetti di inchiostrare se hai già abbastanza inchiostro
        # per giocare la carta più costosa rimasta in mano.
        max_cost_other_cards = get_max_cost_in_hand(card_to_ink)
        
        # Abbiamo già abbastanza inchiostro E siamo almeno a 6
        if ink_total >= max_cost_other_cards and ink_total >= 6:
            return float("-inf")

        # Perché dovremmo inchiostrare
        
        base_score = 0.0
        
        target_cost = ink_total + 1
        has_target_card = any(
            hasattr(c, 'cost') and c.cost == target_cost
            for c in hand if c != card_to_ink
        )
        
        if has_target_card:
            base_score += BONUS_TARGET_CARD
        
        # Bonus "Ramp Generico" (Early game)
        elif ink_total < 4:
            base_score += BONUS_EARLY_RAMP
        
        # Bonus "Ramp Metà Partita"
        elif ink_total < 6:
            base_score += BONUS_MID_RAMP

        # Scegliere la carta peggiore da inchiostrare
        
        
        card_penalty = 0.0
        
        raw_value = 0.0
        if isinstance(card_to_ink, CharacterCard):
            raw_value = (card_to_ink.lore * 2) + card_to_ink.strength + card_to_ink.willpower
        elif hasattr(card_to_ink, 'cost'):
            raw_value = card_to_ink.cost 
        

        cost_delta = card_to_ink.cost - ink_total
            
        if cost_delta <= 0:
                # Caso 1: La carta è GIA' GIOCABILE (costo <= ink attuale)
                # Inchiostrarla è molto male. Applichiamo un moltiplicatore.
            card_penalty = raw_value * 2.0 
        else:
                # Caso 2: La carta NON è ancora giocabile (costo > ink attuale)
                # Penalità = Valore Grezzo / Distanza
                # Più è lontana (delta alto), più la penalità si abbassa.
                # (Aggiungiamo +1 per evitare divisioni per 1 e smussare la curva)
            card_penalty = raw_value / (cost_delta + 1)
        
        final_score = base_score - card_penalty

        if final_score <= 0:
            return float("-inf")
            
        return final_score

    # Filtra prima di chiamare max() per evitare errori su liste vuote
    scored_inks = [(score(act), i, act) for i, act in inks]
    valid_inks = [(s, i, a) for s, i, a in scored_inks if s > float("-inf")]
    
    if not valid_inks:
        return None, 0.0  

    best_score, best_idx, best_action = max(valid_inks, key=lambda x: x[0])

    return best_idx, best_score
    
def play_character_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    plays = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, PlayCardAction) and isinstance(act.card, CharacterCard) 
    ]
    if not plays:
        return None, 0.0
    player = gamestate.engine.currentPlayer
    available = gamestate.engine.currentPlayer.ready_ink
    hand_size = len(gamestate.engine.currentPlayer.hand)
    def score(a):
        c = a.card 
        if c.cost > available:  # Not playable
            return float("-inf")
        
        base = (c.lore * 2) + c.strength + c.willpower # Base score

        if c.cost == available: # Bonus spend all ink
            base += 4
       
        if hand_size <= 2: # Bonus small hands
            base += 6  

        return base

    # discard negative scored plays
    scored_plays = [(score(act), i, act) for i, act in plays if score(act) > float("-inf")]
    
    if not scored_plays:
        return None, 0.0
        
    best_score, best_idx, best_action = max(scored_plays, key=lambda x: x[0])
    return best_idx, best_score


def play_item_heuristic(actions, gamestate):
    """Valuta le carte Action che giocano un Item (es. Dinglehopper)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink

    # Filtra SOLO per PlayAction E ItemCard
    plays = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, PlayCardAction) and isinstance(act.card, ItemCard)
    ]
    
    if not plays:
        return None, 0.0
    
    player = gamestate.engine.currentPlayer
    available = gamestate.engine.currentPlayer.ready_ink
    hand_size = len(gamestate.engine.currentPlayer.hand)
    
    BONUS_SPEND_ALL = 4

    def score(a):
        c = a.card 
        
        # Not playable
        if c.cost > available:
            return float("-inf")

        # Playability score
        base = c.cost * 2  
        
        if c.cost == available:
            base += BONUS_SPEND_ALL
        
        # Bonus small hands
        if hand_size <= 2:
            base += 6  
            
        return base


    scored_plays = [(score(act), i, act) for i, act in plays if score(act) > float("-inf")]
    
    if not scored_plays:
        return None, 0.0
        
    best_score, best_idx, best_action = max(scored_plays, key=lambda x: x[0])
    
    return best_idx, best_score

def avoid_ink_evasion_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    inks = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, InkAction)
    ]
    if not inks:
        return None
    def score(a):
        c = a.card
        if isinstance(c, CharacterCard):
            evasive = "Evasive" in c.keywords or "Bodyguard" in c.keywords
            return (c.lore * 3 + (2 if evasive else 0), c.cost)
        else:
            return (3, c.cost)
    best_idx, best_action = min(inks, key=lambda x: score(x[1]))
    return best_idx, score(best_action)


def quest_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    quests = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, QuestAction)
    ]
    if not quests:
        return None, 0.0
    
    my_lore = gamestate.engine.currentPlayer.lore
    opp_lore = gamestate.engine.currentOpponent.lore
    my_chars = gamestate.engine.currentPlayer.in_play_characters
    opponent_chars = gamestate.engine.currentOpponent.in_play_characters

    def quest_score(a):
        card = a.card
        # Possible lore gained from base questing value
        score = card.lore * 2  
        # Push quest if you are near winning
        if my_lore + card.lore >= 20:
            return 1000.0
        if my_lore >= 16:
            score += card.lore * 3
        if my_lore >= opp_lore:
            score += 4 


        # Penalty if opponent has ready characters that can block and potentially banish
        for opp in opponent_chars:
            if opp.ready and opp.card.strength >= card.willpower:
                score -= card.lore * 2  # rischia banish

    
        # bonus se il tuo board è più grande
        if len(my_chars) > len(opponent_chars):
            score += 2

        return score
    best_idx, best_action = max(quests, key=lambda x: quest_score(x[1]))
    best_score = quest_score(best_action)
    # Choose the quest action with the highest score
    return best_idx, best_score



def deny_lore_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    challengers = [
        (i, act) for i, act in enumerate(real_actions)
        if i in actions and isinstance(act, ChallengeAction)
    ]
    targets = [
        (i, act) for i, act in enumerate(real_actions)
        if i in actions and isinstance(act, ChallengeTargetAction)
    ]

    opp = gamestate.engine.currentOpponent
    if not opp:
        return None, 0.0

    # Se l'oppo è vicino a vincere, provo a rimuovere le sue minacce di lore
    if opp.lore >= 16:
        if targets:
            best_idx, best_action = max(
                targets, key=lambda x: getattr(x[1].card, "lore", 0)
            )
            score = getattr(best_action.card, "lore", 0) * 2.0
            return best_idx, score

        if challengers:
            def chall_score(a):
                c = a.card
                return c.strength + c.willpower * 0.5
            best_idx, best_action = max(challengers, key=lambda x: chall_score(x[1]))
            return best_idx, chall_score(best_action)

    return None, 0.0

def tempo_push_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    quests = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, QuestAction)
    ]
    if not quests:
        return None, 0.0
    
    my_chars = len(gamestate.engine.currentPlayer.in_play_characters)
    opp_chars = len(gamestate.engine.currentOpponent.in_play_characters)
    if my_chars > opp_chars:
        # Agro
        best_idx, best_action = max(
            quests, key=lambda x: getattr(x[1].card, "lore", 0)
        )
        return best_idx, getattr(best_action.card, "lore", 0)
    else:
        # Control 
        best_idx, best_action = min(
            quests, key=lambda x: getattr(x[1].card, "lore", 0)
        )
        return best_idx, getattr(best_action.card, "lore", 0)



def endturn_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()
    ends = [(i, a) for i, a in enumerate(real_actions) if isinstance(a, PassAction)]
    if not ends:
        return None, 0.0
    return ends[0][0], 0.0



def challenge_efficiency_heuristic(actions, gamestate):
    # Ottieni le azioni reali mappate agli indici
    real_actions = gamestate.engine.get_actions()

    # Fase 1: Scegliere un ATTACCANTE (se siamo in GamePhase.MAIN)
    if gamestate.engine.phase == GamePhase.MAIN:
        challengers = [
            (i, act) for i, act in enumerate(real_actions)
            if isinstance(act, ChallengeAction)
        ]
        
        if not challengers:
            return None, 0.0 # Nessun attaccante disponibile

        def challenger_value(challenger):
            my = challenger.card
            # Valore basato solo sulle statistiche
            return my.strength + my.willpower * 0.7

        best_idx, best_action = max(challengers, key=lambda x: challenger_value(x[1]))
        return best_idx, challenger_value(best_action)

    # Fase 2: Scegliere un BERSAGLIO (se siamo in GamePhase.CHALLENGING)
    elif gamestate.engine.phase == GamePhase.CHALLENGING:
        targets = [
            (i, act) for i, act in enumerate(real_actions)
            if isinstance(act, ChallengeTargetAction)
        ]

        if not targets:
            return None, 0.0 # Nessun bersaglio disponibile

        # Ottieni l'attaccante dallo stato del gioco, NON da una variabile globale
        challenger_in_play = gamestate.engine.current_challenger
        if not challenger_in_play:
             # Se per qualche motivo l'attaccante non è impostato, non possiamo valutare
             return None, 0.0

        me = challenger_in_play.card # La carta del nostro attaccante
        my_lore = gamestate.engine.currentPlayer.lore
        opp_lore = gamestate.engine.currentOpponent.lore

        def target_value(t):
            opp = t.card # La carta del bersaglio
            
            # Se il bersaglio è evasivo e io non lo sono -> impossibile sfidare
            # (Nota: questa logica è già gestita da get_actions in game.py, 
            #  ma è una buona doppia verifica)
            is_opp_evasive = any(k == "Evasive" for k in opp.keywords) # Semplificato, usa la tua logica has_evasive se disponibile
            is_me_evasive = any(k == "Evasive" for k in me.keywords)
            
            if is_opp_evasive and not is_me_evasive:
                return -999  

            score = 0

            # Analisi del trade
            my_willpower = getattr(me, "willpower", 0)
            opp_strength = getattr(opp, "strength", 0)
            opp_willpower = getattr(opp, "willpower", 0)
            my_strength = getattr(me, "strength", 0) + challenger_in_play.challenger_keyword # Includi keyword Challenger+

            my_survives = my_willpower > opp_strength
            opp_dies = opp_willpower <= my_strength

            if opp_dies and my_survives:
                score += 6  # Trade pulito -> ottimo
            elif opp_dies and not my_survives:
                score += 3  # Trade alla pari -> ok
            elif not opp_dies and my_survives:
                score += 1  # Danno parziale -> va bene
            else:
                score -= 2  # Trade negativo

            # Punti lore -> importanti se sei indietro
            lore_weight = 3 if my_lore < opp_lore else 2
            score += getattr(opp, "lore", 0) * lore_weight

            # Ricompensa l'eliminazione di bersagli con forza alta
            if opp_strength >= 3:
                score += 2

            # Se sono vicino a vincere, evito i trade negativi
            if my_lore >= 17:
                score -= 3 if not my_survives else 0

            return score

        best_idx, best_action = max(targets, key=lambda x: target_value(x[1]))
        return best_idx, target_value(best_action)

    # Se non siamo in nessuna delle due fasi, non fare nulla
    return None, 0.0



def healing_ability_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()


    healing_actions = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, TriggeredAbilityAction)
        and isinstance(act.ability, HealingTriggeredAbility)
    ]

    if not healing_actions:
        return None, 0.0
    
    current_player = gamestate.engine.currentPlayer
    opponent_player = gamestate.engine.currentOpponent

    # Check if ANY allied targets exist AT ALL ---
    can_heal_ally = any(ch.damage > 0 for ch in current_player.in_play_characters)
    if not can_heal_ally:
        # If the only possible targets would be opponents, don't even consider activating.
        # Assign a negative score to actively discourage it.
        # Find the index of the first healing action to return it with a bad score.
        first_heal_idx = healing_actions[0][0]
        return first_heal_idx, -100.0

    def evaluate_healing(act):
 
        healing_power = act.ability.healing_power
        current_player = gamestate.engine.currentPlayer

        # consider only damaged characters and ALLY
        damaged_chars = [
            ch for ch in current_player.in_play_characters
            if ch.damage > 0
        ]
        if not damaged_chars:
            return 0.0

        best_score = 0.0
        for ch in damaged_chars:
            effective_heal = min(healing_power, ch.damage)
            # based on lore and willpower
            weight = ch.card.lore + ch.card.strength + ch.card.willpower
            score = effective_heal * weight *2
            if score > best_score:
                best_score = score
        return best_score

  
    scored_actions = [(evaluate_healing(act), i, act) for i, act in healing_actions]
    best_score, best_index, best_action = max(scored_actions, key=lambda x: x[0])

    if best_score <= 0.0:
        return None, 0.0  

    return best_index, evaluate_healing(best_action)


def damage_ability_heuristic(actions, gamestate):
    real_actions = gamestate.engine.get_actions()

    damage_actions = [
        (i, act) for i, act in enumerate(real_actions)
        if isinstance(act, TriggeredAbilityAction)
        and isinstance(act.ability, DamageTriggeredAbility)
    ]

    if not damage_actions:
        return None, 0.0

    opponent = gamestate.engine.currentOpponent
    opp_chars = opponent.in_play_characters

    if not opp_chars:
        return None, 0.0

    def evaluate_damage(act):
        damage_power = act.ability.damage_power

        best_score = float("-inf")
        for ch in opp_chars:
            # Stat target
            total_hp = ch.card.willpower
            current_damage = ch.damage
            remaining_hp = total_hp - current_damage
            effective_damage = min(damage_power, remaining_hp)

            # Clean kill? 
            clean_kill = effective_damage >= remaining_hp

            # Punteggio base: valore del pezzo
            base_value = (
                ch.card.lore * 3 +           
                ch.card.strength +      
                ch.card.willpower            
            )

            # Bonus se clean kill
            if clean_kill:
                score = base_value * 2.0
            else:
                # danno parziale → peso ridotto
                score = base_value * (effective_damage / max(remaining_hp, 1))

            # Penalizza overkill enorme (danno >> vita residua)
            overkill = damage_power - remaining_hp
            if overkill > 0:
                score -= overkill * 0.5

            if score > best_score:
                best_score = score

        return best_score

    scored_actions = [(evaluate_damage(act), i, act) for i, act in damage_actions]
    best_score, best_index, best_action = max(scored_actions, key=lambda x: x[0])

    if best_score <= 0.0:
        return None, 0.0  

    return best_index, best_score







# --- Inizio Euristiche per ActionCard ---

def _evaluate_target_damage(damage_power, gamestate):
    """Helper: Valuta il punteggio per un'abilità che infligge danno a un bersaglio."""
    opponent = gamestate.engine.currentOpponent
    opp_chars = opponent.in_play_characters
    if not opp_chars: return 0.0

    best_score = float("-inf")
    for ch in opp_chars:
        total_hp = ch.card.willpower
        current_damage = ch.damage
        remaining_hp = total_hp - current_damage
        effective_damage = min(damage_power, remaining_hp)
        clean_kill = effective_damage >= remaining_hp and remaining_hp > 0
        base_value = (ch.card.lore * 3 + ch.card.strength * 2 + ch.card.willpower)
        score = (base_value * 2.0) if clean_kill else (base_value * (effective_damage / max(remaining_hp, 1)))
        if score > best_score: best_score = score
    return best_score if best_score > float("-inf") else 0.0

def play_target_damage_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che infliggono danno a un bersaglio (es. Fire the Cannons, Smash)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    
    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], DamageTriggeredAbility)):
            plays.append((i, act))
            
    if not plays:
        return None, 0.0

    def score(action):
        ability = action.card.abilities[0]
        return _evaluate_target_damage(ability.damage_power, gamestate)

    best_idx, best_action = max(plays, key=lambda x: score(x[1]))
    best_score = score(best_action)
    return (best_idx, best_score) if best_score > 0 else (None, 0.0)

def play_draw_card_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che fanno pescare (es. Friends on the Other Side)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    player = gamestate.engine.currentPlayer
    hand_size = len(player.hand)

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], DrawCardsActionAbility)): #
            plays.append((i, act))
            
    if not plays:
        return None, 0.0

    def score(action):
        ability = action.card.abilities[0]
        base_score = ability.cards_to_draw * 6  # Pescare è forte
        if hand_size <= 2: base_score += 5 # Bonus se a mano vuota
        return base_score

    best_idx, best_action = max(plays, key=lambda x: score(x[1]))
    return best_idx, score(best_action)

def play_ramp_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che accelerano l'inchiostro (es. One Jump Ahead)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    player = gamestate.engine.currentPlayer
    total_ink = player.ready_ink + player.exerted_ink

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], InkTopCardAbility)): #
            plays.append((i, act))

    if not plays:
        return None, 0.0

    # Punteggio fisso basato sulla fase del gioco
    score = 0.0
    if total_ink < 4: score = 15.0  # Priorità alta a inizio partita
    elif total_ink < 7: score = 8.0   # Buona priorità
    
    if score == 0.0: return None, 0.0 # Non giocarla in late game

    # Prendi la prima (e unica) azione di ramp trovata
    best_idx, best_action = plays[0]
    return best_idx, score

def play_aoe_damage_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che infliggono danno a tutti i nemici (es. Grab Your Sword)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    opponent = gamestate.engine.currentOpponent

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], DamageAllOpponentsAbility)): #
            plays.append((i, act))
            
    if not plays or not opponent.in_play_characters:
        return None, 0.0

    def score(action):
        ability = action.card.abilities[0]
        score_val = 0.0
        for ch in opponent.in_play_characters:
            remaining_hp = ch.card.willpower - ch.damage
            if ability.damage_power >= remaining_hp and remaining_hp > 0:
                score_val += (ch.card.lore * 5 + ch.card.strength * 2 + 10) # Bonus uccisione
            else:
                score_val += ability.damage_power * 2 # Danno parziale
        return score_val

    best_idx, best_action = max(plays, key=lambda x: score(x[1]))
    best_score = score(best_action)
    return (best_idx, best_score) if best_score > 0 else (None, 0.0)

def play_aoe_heal_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che curano tutti gli alleati (es. Hakuna Matata)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    player = gamestate.engine.currentPlayer

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], HealAllCharactersAbility)): #
            plays.append((i, act))

    if not plays or not player.in_play_characters:
        return None, 0.0

    def score(action):
        ability = action.card.abilities[0]
        effective_heal = 0
        for ch in player.in_play_characters:
            effective_heal += min(ch.damage, ability.healing_power)
        
        # Non giocare se non c'è (quasi) nulla da curare
        return effective_heal * 3.0

    best_idx, best_action = max(plays, key=lambda x: score(x[1]))
    best_score = score(best_action)
    return (best_idx, best_score) if best_score >= 2.0 else (None, 0.0) # Soglia minima di cura

def play_target_heal_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che curano un bersaglio (es. Healing Glow)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    player = gamestate.engine.currentPlayer

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], TargetedHealingAbility)):
            plays.append((i, act))

    if not plays:
        return None, 0.0
    
    can_heal_ally = any(ch.damage > 0 for ch in player.in_play_characters)
    if not can_heal_ally:
        # If the only possible targets generated by get_actions would be opponents,
        # score this play extremely negatively.
        first_play_idx = plays[0][0]
        return first_play_idx, -100.0

    # Trova il miglior bersaglio da curare
    best_target_score = 0.0
    damaged_chars = [ch for ch in player.in_play_characters if ch.damage > 0]
    if not damaged_chars:
        return None, 0.0 # Non giocare se non c'è nulla da curare

    for ch in damaged_chars:
        # Punteggio = Valore del personaggio * quanto lo curi
        valore = ch.card.lore * 3 + ch.card.strength + ch.card.willpower
        score = valore * min(ch.damage, 2) # 2 è il potere di Healing Glow
        if score > best_target_score:
            best_target_score = score

    if best_target_score == 0.0:
        return None, 0.0

    # Punteggio finale = valore del bersaglio - costo della carta
    # (Usa l'azione con il costo più basso se ce ne sono multiple)
    best_idx, best_action = min(plays, key=lambda x: x[1].card.cost)
    return best_idx, best_target_score - best_action.card.cost

def play_banish_item_action_heuristic(actions, gamestate):
    """Valuta le carte Azione che rimuovono Oggetti (es. Break)."""
    real_actions = gamestate.engine.get_actions()
    available_ink = gamestate.engine.currentPlayer.ready_ink
    opponent = gamestate.engine.currentOpponent

    plays = []
    for i, act in enumerate(real_actions):
        if (isinstance(act, PlayCardAction) and 
            isinstance(act.card, ActionCard) and 
            act.card.cost <= available_ink and
            act.card.abilities and isinstance(act.card.abilities[0], BanishItemAbility)):
            plays.append((i, act))

    if not plays or not opponent.in_play_items:
        return None, 0.0 # Non giocare se l'avversario non ha Oggetti

    # Trova il miglior Oggetto da rompere (quello che costa di più)
    best_target_score = 0.0
    for item in opponent.in_play_items:
        # Punteggio = Costo dell'oggetto * 2 
        score = item.card.cost * 2.0
        if score > best_target_score:
            best_target_score = score

    if best_target_score == 0.0:
        return None, 0.0

    # Punteggio finale = valore del bersaglio - costo della carta
    best_idx, best_action = min(plays, key=lambda x: x[1].card.cost)
    return best_idx, best_target_score - best_action.card.cost



# --- Fine Nuove Euristiche ---



###########################################################################
ALL_HEURISTICS = [
    mulligan_heuristic, #
    ink_heuristic, #
    
    # Euristiche per GIOCARE CARTE (in competizione tra loro)
    play_character_heuristic,
    play_draw_card_action_heuristic,
    play_ramp_action_heuristic,
    play_target_damage_action_heuristic,
    play_aoe_damage_action_heuristic,
    play_aoe_heal_action_heuristic,
    play_target_heal_action_heuristic,
    play_banish_item_action_heuristic,
    play_item_heuristic, #
    
    # Euristiche per AZIONI SUL CAMPO
    quest_heuristic, #
    deny_lore_heuristic, #
    tempo_push_heuristic, #
    challenge_efficiency_heuristic, #
    
    # Euristiche per ABILITÀ ATTIVABILI
    healing_ability_heuristic, #
    damage_ability_heuristic, #
    
    # Fallback
    endturn_heuristic, #
]
def combined_heuristic(state, player=None):
    actions = state.legal_actions()

    best_idx = None
    best_score = float("-inf")
    best_heuristic = None

    for heuristic in ALL_HEURISTICS:
        idx, score = heuristic(actions, state)
        if idx is not None and score > best_score:
            best_idx, best_score = idx, score
            #best_heuristic = heuristic.__name__

    if best_idx is None:
        return 0.0  
    
    return best_score




def get_heuristic_scores_for_action(chosen_action_index, state):
    """
    Ricalcola e restituisce i punteggi di tutte le euristiche per una
    specifica azione scelta. Utile per il logging.
    """
    scores = {}
    # Ottieni gli indici delle azioni legali (necessari per le euristiche)
    legal_indices = state.legal_actions() 
    
    for heuristic in ALL_HEURISTICS:
        # Chiama l'euristica passando gli indici legali
        idx, score = heuristic(legal_indices, state) 
        
        # Se l'euristica ha scelto la stessa azione che stiamo analizzando
        # E ha dato un punteggio valido
        if idx == chosen_action_index and score > float("-inf"):
             scores[heuristic.__name__] = score
             
    # Trova l'euristica che ha dato il punteggio massimo per questa azione
    winning_heuristic = None
    winning_score = float("-inf")
    if scores:
        winning_heuristic, winning_score = max(scores.items(), key=lambda item: item[1])
        
    return winning_heuristic, winning_score, scores 



# In heuristic.py

def static_state_evaluation_heuristic(state, player_id):
    if player_id == 0:
        my_player = state.engine.p1
        opp_player = state.engine.p2
    else:
        my_player = state.engine.p2
        opp_player = state.engine.p1

    my_score = 0.0
    opp_score = 0.0

    my_score += my_player.lore * 30.0 # Winning condition
    opp_score += opp_player.lore * 30.0

    for char in my_player.in_play_characters: # Board Presence
        char_value = (char.card.lore * 10.0) + \
                     (char.card.strength * 3.0) + \
                     (char.card.willpower * 2.0)
        char_value -= (char.damage * 4.0) # Damage Penalty
        if char.ready:
            char_value += 3.0
        if not char.dry:
            char_value *= 0.5 
        my_score += char_value

    for char in opp_player.in_play_characters:
        char_value = (char.card.lore * 10.0) + \
                     (char.card.strength * 3.0) + \
                     (char.card.willpower * 2.0)
        char_value -= (char.damage * 4.0)
        if char.ready:
            char_value += 3.0
        if not char.dry:
            char_value *= 0.5
        opp_score += char_value

    # Hand Size
    my_score += len(my_player.hand) * 5.0 
    opp_score += len(opp_player.hand) * 5.0
    # Ink Presence
    my_ink = my_player.ready_ink + my_player.exerted_ink
    opp_ink = opp_player.ready_ink + opp_player.exerted_ink
    
    # After 8 ink, diminishing returns
    my_score += min(my_ink, 8) * 7.0
    opp_score += min(opp_ink, 8) * 7.0

    # Item Presence
    for item in my_player.in_play_items:
        my_score += (item.card.cost * 3.0) + (2.0 if item.ready else 0.0)
    for item in opp_player.in_play_items:
        opp_score += (item.card.cost * 3.0) + (2.0 if item.ready else 0.0)

    return my_score - opp_score



