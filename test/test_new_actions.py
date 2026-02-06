#!/usr/bin/python3
import sys
from game import Game
from lorcana.contestant import Contestant
from controller import RandomController, EnvironmentController
from deck import Deck
from decklists import (
    amber_amethyst, sapphire_steel, # Mazzi per i contestant
    olaf, dinglehopper, # Carte per i test
    healing_glow, break2 # Le NUOVE carte da testare
)
from inplay_character import InPlayCharacter
from inplay_card import InPlayItem
from action import PlayCardAction, AbilityTargetAction, AbilityTargetItemAction
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
    c1 = Contestant(amber_amethyst, RandomController("P1_Dummy"))
    c2 = Contestant(sapphire_steel, RandomController("P2_Dummy"))
    
    game = Game(c1, c2, EnvironmentController())
    
    # Saltiamo le fasi iniziali (Mulligan, Draw)
    game.phase = GamePhase.MAIN
    game.p1.deck.cards = [olaf, olaf, olaf] 
    game.p2.deck.cards = [olaf, olaf, olaf]
    
    # Diamo ai giocatori abbastanza inchiostro per i test
    game.p1.ready_ink = 20
    game.p2.ready_ink = 20
    
    return game, game.p1, game.p2

if __name__ == '__main__':
    print("Avvio test delle Nuove Carte Azione (Heal & Break)...")

    # --- Test 1: 'Healing Glow' (Cura Bersagliata) ---
    game, p1, p2 = setup_game()
    test_card_heal = healing_glow #
    # Mettiamo un personaggio danneggiato in gioco per P1
    target_char = InPlayCharacter(olaf, damage=2)
    p1.in_play_characters = [target_char]
    p1.hand = [test_card_heal]
    
    # Step 1: Gioca la carta
    game.process_action(PlayCardAction(test_card_heal))
    
    run_test(
        "Healing Glow (Fase Targeting)",
        game.phase == GamePhase.CHOOSE_TARGET, #
        "Il gioco non è entrato in fase CHOOSE_TARGET"
    )
    
    # Step 2: Trova e scegli il bersaglio
    actions = game.get_actions()
    # Troviamo la prima (e unica) azione che bersaglia un personaggio di P1
    target_action_heal = next(
        (a for a in actions if isinstance(a, AbilityTargetAction) and a.player == PlayerTurn.PLAYER1), 
        None
    )
            
    run_test(
        "Healing Glow (Azione Trovata)",
        target_action_heal is not None,
        "Non è stata trovata un'Azione di targeting (AbilityTargetAction) valida per P1"
    )

    game.process_action(target_action_heal)
    
    run_test(
        "Healing Glow (Cura Applicata)",
        target_char.damage == 0, # Curato da 2 a 0
        f"Danno personaggio dovrebbe essere 0, è {target_char.damage}"
    )
    run_test(
        "Healing Glow (Scartata dopo uso)",
        test_card_heal in p1.discard, #
        "La carta Azione non è finita negli scarti dopo il targeting"
    )
    run_test(
        "Healing Glow (Fase Tornata a MAIN)",
        game.phase == GamePhase.MAIN, #
        "Il gioco non è tornato in fase MAIN"
    )

    print("-" * 20)

    # --- Test 2: 'Break' (Banish Oggetto Bersagliato) ---
    game, p1, p2 = setup_game()
    test_card_break = break2 #
    # Mettiamo un oggetto in gioco per P2
    target_item = InPlayItem(dinglehopper)
    p2.in_play_items = [target_item]
    p1.hand = [test_card_break]

    # Step 1: Gioca la carta
    game.process_action(PlayCardAction(test_card_break))
    
    run_test(
        "Break (Fase Targeting)",
        game.phase == GamePhase.CHOOSE_TARGET, #
        "Il gioco non è entrato in fase CHOOSE_TARGET"
    )
    
    # Step 2: Trova e scegli il bersaglio
    actions = game.get_actions()
    # Troviamo la prima (e unica) azione che bersaglia un oggetto di P2
    target_action_break = next(
        (a for a in actions if isinstance(a, AbilityTargetItemAction) and a.player == PlayerTurn.PLAYER2), 
        None
    )
            
    run_test(
        "Break (Azione Trovata)",
        target_action_break is not None,
        "Non è stata trovata un'Azione di targeting (AbilityTargetItemAction) valida per P2"
    )

    game.process_action(target_action_break)
    
    run_test(
        "Break (Oggetto Rimosso da 'in_play')",
        len(p2.in_play_items) == 0, #
        "L'oggetto non è stato rimosso da in_play_items"
    )
    run_test(
        "Break (Oggetto finito in 'discard')",
        dinglehopper in p2.discard, #
        "L'oggetto non è stato aggiunto agli scarti di P2"
    )
    run_test(
        "Break (Carta Azione Scartata)",
        test_card_break in p1.discard, #
        "La carta 'Break' non è finita negli scarti di P1"
    )
    run_test(
        "Break (Fase Tornata a MAIN)",
        game.phase == GamePhase.MAIN, #
        "Il gioco non è tornato in fase MAIN"
    )

    print("\n--- Tutti i nuovi test delle Azioni sono stati superati! ---")