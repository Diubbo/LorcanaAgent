#!/usr/bin/python3
import sys
from game import Game
from contestant import Contestant
from controller import RandomController, EnvironmentController
from deck import Deck
from decklists import (
    amber_amethyst, sapphire_steel, # Mazzi per i contestant
    olaf, stitch, # Carte personaggio per i test
    friends_on_the_other_side, hakuna_matata, one_jump_ahead, 
    grab_your_sword, fire_the_cannons
)
from inplay_character import InPlayCharacter
from action import PlayCardAction, AbilityTargetAction
from game_enums import GamePhase, PlayerTurn

# Semplice helper per i test
def run_test(test_name, condition, error_message=""):
    if condition:
        print(f"✅ [PASS] {test_name}")
    else:
        print(f"❌ [FAIL] {test_name} - {error_message}")
        sys.exit(1) # Interrompe l'esecuzione in caso di fallimento

def setup_game():
    """Crea un'istanza di gioco pulita per ogni test."""
    # Usiamo mazzi qualsiasi, tanto li sovrascriviamo
    c1 = Contestant(amber_amethyst, RandomController("P1_Dummy"))
    c2 = Contestant(sapphire_steel, RandomController("P2_Dummy"))
    
    # Usiamo EnvironmentController per gestire le fasi automatiche
    game = Game(c1, c2, EnvironmentController())
    
    # Saltiamo le fasi iniziali (Mulligan, Draw)
    game.phase = GamePhase.MAIN
    game.p1.deck.cards = [olaf, stitch, olaf, stitch, olaf] # Un mazzo fittizio
    game.p2.deck.cards = [olaf, stitch, olaf, stitch, olaf]
    
    # Diamo ai giocatori abbastanza inchiostro per i test
    game.p1.ready_ink = 20
    game.p2.ready_ink = 20
    
    return game, game.p1, game.p2

if __name__ == '__main__':
    print("Avvio test delle Carte Azione (Gruppo 1 & 2)...")
    
    # --- Test 1: 'Friends On The Other Side' (Pesca 2) ---
    game, p1, p2 = setup_game()
    test_card = friends_on_the_other_side
    p1.hand = [test_card]
    p1.deck.cards = [olaf, stitch] # Mazzo con 2 carte
    initial_hand_size = len(p1.hand) # 1
    
    game.process_action(PlayCardAction(test_card))
    
    run_test(
        "Friends On The Other Side (Pesca 2)",
        len(p1.hand) == initial_hand_size - 1 + 2, # 1 - 1 + 2 = 2
        f"Mano dovrebbe avere 2 carte, ne ha {len(p1.hand)}"
    )
    run_test(
        "Friends On The Other Side (Scartata)",
        test_card in p1.discard,
        "La carta non è finita nella pila degli scarti"
    )

    # --- Test 2: 'One Jump Ahead' (Inchiostra top card) ---
    game, p1, p2 = setup_game()
    test_card = one_jump_ahead
    card_to_ink = olaf # Sappiamo che questa è la prima carta
    p1.hand = [test_card]
    p1.deck.cards = [card_to_ink, stitch]
    initial_deck_size = p1.deck.get_total_cards() # 2
    
    game.process_action(PlayCardAction(test_card))
    
    run_test(
        "One Jump Ahead (Inchiostra)",
        p1.exerted_ink == 3, # 2 dal costo della carta + 1 dall'abilità
        f"Inchiostro exerted dovrebbe essere 3 (2 dal costo + 1 dall'abilità), è {p1.exerted_ink}"
    )
    run_test(
        "One Jump Ahead (Mazzo ridotto)",
        p1.deck.get_total_cards() == initial_deck_size - 1, # 1
        "Il mazzo non ha perso una carta"
    )
    run_test(
        "One Jump Ahead (Mano vuota)",
        len(p1.hand) == 0, # Carta giocata, carta inchiostrata
        "La mano non è vuota"
    )
    run_test(
        "One Jump Ahead (Scartata)",
        test_card in p1.discard,
        "La carta non è finita nella pila degli scarti"
    )

    # --- Test 3: 'Hakuna Matata' (Cura tutti i tuoi) ---
    game, p1, p2 = setup_game()
    test_card = hakuna_matata
    p1.hand = [test_card]
    char_to_heal = InPlayCharacter(olaf, damage=2)
    p1.in_play_characters = [char_to_heal]
    
    game.process_action(PlayCardAction(test_card))
    
    run_test(
        "Hakuna Matata (Cura)",
        char_to_heal.damage == 0, # Curato da 2 a 0
        f"Danno personaggio dovrebbe essere 0, è {char_to_heal.damage}"
    )
    run_test(
        "Hakuna Matata (Scartata)",
        test_card in p1.discard,
        "La carta non è finita nella pila degli scarti"
    )

    # --- Test 4: 'Grab Your Sword' (Danno a tutti gli avversari) ---
    game, p1, p2 = setup_game()
    test_card = grab_your_sword
    p1.hand = [test_card]
    target1 = InPlayCharacter(stitch, damage=0) # Stitch ha 2 willpower
    target2 = InPlayCharacter(olaf, damage=0)   # Olaf ha 3 willpower
    p2.in_play_characters = [target1, target2]
    
    game.process_action(PlayCardAction(test_card))
    
    run_test(
        "Grab Your Sword (Danno Target 1)",
        target1.damage == 2, # Danno 2
        f"Danno Target 1 dovrebbe essere 2, è {target1.damage}"
    )
    run_test(
        "Grab Your Sword (Danno Target 2)",
        target2.damage == 2, # Danno 2
        f"Danno Target 2 dovrebbe essere 2, è {target2.damage}"
    )
    run_test(
        "Grab Your Sword (Banish corretto)",
        target1 not in p2.in_play_characters and target2 in p2.in_play_characters,
        "Banish errato (Stitch dovrebbe essere banish, Olaf no)"
    )
    run_test(
        "Grab Your Sword (Scartata)",
        test_card in p1.discard,
        "La carta non è finita nella pila degli scarti"
    )

    # --- Test 5: 'Fire the Cannons!' (Danno bersagliato + Scartata) ---
    # Questo è il test per la correzione del Gruppo 1
    game, p1, p2 = setup_game()
    test_card = fire_the_cannons
    p1.hand = [test_card]
    target_char = InPlayCharacter(olaf, damage=0)
    p2.in_play_characters = [target_char]
    
    # Step 1: Gioca la carta
    game.process_action(PlayCardAction(test_card))
    run_test(
        "Fire the Cannons! (Fase Targeting)",
        game.phase == GamePhase.CHOOSE_TARGET,
        "Il gioco non è entrato in fase CHOOSE_TARGET"
    )
    
    # Step 2: Scegli il bersaglio
    # Troviamo l'azione di targeting corretta
    target_action = None
    for action in game.get_actions():
        if isinstance(action, AbilityTargetAction) and action.target_card == olaf:
            target_action = action
            break
            
    run_test(
        "Fire the Cannons! (Azione Trovata)",
        target_action is not None,
        "Non è stata trovata un'Azione di targeting valida"
    )

    game.process_action(target_action)
    
    run_test(
        "Fire the Cannons! (Danno Applicato)",
        target_char.damage == 2, # Danno 2
        f"Danno personaggio dovrebbe essere 2, è {target_char.damage}"
    )
    run_test(
        "Fire the Cannons! (Scartata dopo uso)",
        test_card in p1.discard, # Test chiave!
        "La carta Azione non è finita negli scarti dopo il targeting"
    )
    run_test(
        "Fire the Cannons! (Fase Tornata a MAIN)",
        game.phase == GamePhase.MAIN,
        "Il gioco non è tornato in fase MAIN"
    )

    print("\n--- Tutti i test delle Azioni sono stati superati! ---")