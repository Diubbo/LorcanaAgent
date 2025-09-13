# heuristic.py
from action import MulliganAction, InkAction, PassAction, PlayCardAction, QuestAction, ChallengeAction, ChallengeTargetAction
from decklists import CharacterCard, ItemCard  



def mulligan_heuristic(actions, gamestate):
    mulligans = [a for a in actions if isinstance(a, MulliganAction)]
    if not mulligans:
        return None, 0.0
    # Keep cards that are cheap (curve 1-3) and mulligan expensive ones
    to_mulligan = [a for a in mulligans if a.card.cost > 4]
    # if i have no low curve cards, mulligan at least one high cost card
    low_curve = any(a.card.cost <= 3 for a in mulligans)
    chosen = None
    if not low_curve and to_mulligan:
        chosen= to_mulligan[0]
    elif to_mulligan:
        chosen= to_mulligan[0]
    
    # Default: mulligan cards over cost 4
    return chosen, 1.0 if chosen else (None, 0.0)

def ink_heuristic(actions, gamestate):
    inks = [a for a in actions if isinstance(a, InkAction)]
    if not inks:
        return None, 0.0
    
    ink_total = gamestate.currentPlayer.ink
    if ink_total >3 and gamestate.currentPlayer.hand_size < 2:
        # Don't ink if you have enough ink and few cards
        return None, 0.0
    if ink_total < 6:
        # Early game → ink high cost cards
        return max(inks, key=lambda a: a.card.cost), 1.0
    else:
        # Late game → ink low cost cards 
        return min(inks, key=lambda a: a.card.cost), 1.0

def play_heuristic(actions, gamestate):
    plays = [a for a in actions if isinstance(a, PlayCardAction)]
    if not plays:
        return None, 0.0
    
    available = gamestate.currentPlayer.ink - gamestate.currentPlayer.exerted_ink
    char_plays = [a for a in plays if isinstance(a.card, CharacterCard)]
    # Prefer playing characters if possible
    if char_plays:
        chosen = max(char_plays, key=lambda a: (a.card.lore, a.card.strength, a.card.cost <= available))
    else:
        chosen = min(plays, key=lambda a: abs(a.card.cost - available))

    return chosen, 1.0

def quest_heuristic(actions, gamestate):
    quests = [a for a in actions if isinstance(a, QuestAction)]
    if not quests:
        return None, 0.0

    def quest_score(a):
        card = a.card
        # Possible lore gained from base questing value
        score = card.lore * 2  
        # Push quest if you are near winning
        if gamestate.currentPlayer.lore >= 16:
            score += card.lore * 3
    
        # Penalty if opponent has ready characters that can block and potentially banish
        opponent_chars = gamestate.currentOpponent.in_play_characters
        for opp in opponent_chars:
            if opp.ready and opp.strength >= card.willpower:
                score -= card.lore * 2  # rischia banish

        # Bonus for high willpower cards (harder to banish)
        if card.willpower >= 4:
            score += 1

        return score
    chosen = max(quests, key=quest_score)
    # Choose the quest action with the highest score
    return chosen, quest_score(chosen)


def deny_lore_heuristic(actions, gamestate):
    challengers = [a for a in actions if isinstance(a, ChallengeAction)]
    targets = [a for a in actions if isinstance(a, ChallengeTargetAction)]

    # if opponent is close to winning, try to challenge their highest lore character
    if challengers and gamestate.currentOpponent.lore >= 16:
        chosen = max(challengers, key=lambda targets: targets.card.lore)
        return chosen, 2.0
    return None, 0.0

def tempo_push_heuristic(actions, gamestate):
    quests = [a for a in actions if isinstance(a, QuestAction)]
    if not quests:
        return None, 0.0
    
    my_chars = len(gamestate.currentPlayer.in_play_characters)
    opp_chars = len(gamestate.currentOpponent.in_play_characters)

    if my_chars > opp_chars:
        return max(quests, key=lambda a: a.card.lore),1.0  # agro
    else:
        return min(quests, key=lambda a: a.card.lore),1.0  # control



def endturn_heuristic(actions, gamestate):
    ends = [a for a in actions if isinstance(a, PassAction)]
    return (ends[0], 0.5) if ends else (None, 0.0)

def challenge_efficiency_heuristic(actions, gamestate=None):
    challengers = [a for a in actions if isinstance(a, ChallengeAction)]
    targets = [a for a in actions if isinstance(a, ChallengeTargetAction)]

    # Scenario 1: choosing the CHALLENGER
    if challengers:
        def challenger_value(challenger):
            my = challenger.card
            # euristica migliorabile considera solo forza e willpower
            return my.strength + my.willpower * 0.5

        chosen = max(challengers, key=challenger_value)
        return chosen, challenger_value(chosen)

    # Scenario 2: choosing the TARGET           
    if targets:
        def target_value(t):
            opp = t.card
            trade = 0
           # target evalutation based on lore and strength
            trade += opp.lore * 2
            if opp.strength > 3:  # minaccia
                trade += 2
            # avoid tank
            trade -= opp.willpower * 0.5
            return trade

        chosen = max(targets, key=target_value)
        return chosen, target_value(chosen)

    return None, 0.0






###########################################################################
ALL_HEURISTICS = [
    mulligan_heuristic,
    ink_heuristic,
    play_heuristic,
    quest_heuristic,
    deny_lore_heuristic,
    tempo_push_heuristic,
    endturn_heuristic,
    challenge_efficiency_heuristic,
]

def combined_heuristic(state, player):

    actions = state.legal_actions()

    best_action = None
    best_score = float("-inf")

    for heuristic in ALL_HEURISTICS:
        try:
            action, score = heuristic(actions, state)
        except TypeError:
            action = heuristic(actions, state)
            score = 1.0 if action else 0.0

        if action and score > best_score:
            best_action, best_score = action, score

    # neutral score if no action found
    return best_score if best_action else 0.0

