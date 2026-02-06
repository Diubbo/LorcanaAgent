#!/usr/bin/python3
import sys
from game import Game
from lorcana.contestant import Contestant
from controller import RandomController, EnvironmentController
from deck import Deck
from decklists import (
    amber_amethyst, sapphire_steel, # Mazzi per i contestant
    olaf, dinglehopper, magic_golden_flower # Le carte chiave per il test
)
from inplay_character import InPlayCharacter
from inplay_card import InPlayItem
from action import (
    PlayCardAction, TriggeredAbilityAction, AbilityTargetAction
)
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
    
    game.phase = GamePhase.MAIN
    game.p1.ready_ink = 20
    game.p2.ready_ink = 20
    
    return game, game.p1, game.p2

if __name__ == '__main__':
    print("Avvio test sull'utilizzo degli Oggetti (Dinglehopper)...")

    game, p1, p2 = setup_game()
    
    # Setup: Un personaggio danneggiato (Olaf) in gioco
    # e un Dinglehopper in mano
    char_to_heal = InPlayCharacter(olaf, damage=2) # Olaf ha 2 danni
    p1.in_play_characters = [char_to_heal]
    p1.hand = [dinglehopper]

    # --- Test 1: Giocare l'Oggetto dalla Mano ---
    game.process_action(PlayCardAction(dinglehopper))

    run_test(
        "Dinglehopper (Gioca dalla mano)",
        len(p1.hand) == 0,
        "Il Dinglehopper non è stato rimosso dalla mano"
    )
    run_test(
        "Dinglehopper (Appare in gioco)",
        len(p1.in_play_items) == 1 and p1.in_play_items[0].card == dinglehopper,
        "Il Dinglehopper non è apparso in 'in_play_items'"
    )
    item_in_play = p1.in_play_items[0]
    run_test(
        "Dinglehopper (Appare 'Ready')",
        item_in_play.ready == True, #
        "L'oggetto non è entrato in gioco 'ready'"
    )

    # --- Test 2: Attivare l'abilità dell'Oggetto ---
    
    # Troviamo l'azione di attivazione
    actions = game.get_actions()
    item_ability_action = next(
        (a for a in actions if isinstance(a, TriggeredAbilityAction) and a.card == dinglehopper),
        None
    )

    run_test(
        "Dinglehopper (Abilità appare in get_actions)",
        item_ability_action is not None,
        "L'abilità attivabile del Dinglehopper non è stata trovata"
    )

    # Attiviamo l'abilità
    game.process_action(item_ability_action)

    run_test(
        "Dinglehopper (Entra in Fase Targeting)",
        game.phase == GamePhase.CHOOSE_TARGET,
        "Il gioco non è entrato in CHOOSE_TARGET dopo l'attivazione"
    )
    run_test(
        "Dinglehopper (Diventa Exerted/Tappato)",
        item_in_play.ready == False, #
        "L'oggetto non è diventato 'exerted' (ready=False) dopo l'attivazione"
    )
    
    # --- Test 3: Scegliere il bersaglio e curare ---
    
    # Troviamo l'azione di targeting
    target_actions = game.get_actions()
    target_olaf_action = next(
        (a for a in target_actions if isinstance(a, AbilityTargetAction) and a.target_card == olaf),
        None
    )
    
    run_test(
        "Dinglehopper (Trova bersaglio valido)",
        target_olaf_action is not None,
        "Non è stata trovata l'azione per bersagliare Olaf"
    )
    
    # Applichiamo la cura
    game.process_action(target_olaf_action)
    
    run_test(
        "Dinglehopper (Effetto applicato - Cura)",
        char_to_heal.damage == 1, # Dinglehopper cura 1 (da 2 a 1)
        f"Olaf dovrebbe avere 1 danno, ne ha {char_to_heal.damage}"
    )
    run_test(
        "Dinglehopper (Ritorna in Fase MAIN)",
        game.phase == GamePhase.MAIN,
        "Il gioco non è tornato in Fase MAIN"
    )
    run_test(
        "Dinglehopper (Pending ability resettata)",
        game.pending_ability is None and game.pending_ability_card is None, #
        "Le abilità in sospeso non sono state resettate"
    )

    # --- Test 4: L'abilità non è più disponibile (perché Exerted) ---
    actions_after_use = game.get_actions()
    item_ability_action_after = next(
        (a for a in actions_after_use if isinstance(a, TriggeredAbilityAction) and a.card == dinglehopper),
        None
    )
    
    run_test(
        "Dinglehopper (Abilità non disponibile post-uso)",
        item_ability_action_after is None,
        "L'abilità dell'oggetto è ancora disponibile anche se 'exerted'"
    )

    print("\n" + "="*30 + "\n")
    print("Avvio test sull'utilizzo degli Oggetti (Magic Golden Flower)...")

    game, p1, p2 = setup_game()
    
    # Setup:
    test_card_flower = magic_golden_flower #
    char_to_heal_2 = InPlayCharacter(olaf, damage=4) # Abbastanza danno per curare 3
    p1.in_play_characters = [char_to_heal_2]
    p1.hand = [test_card_flower]

    # --- Test 1: Giocare l'Oggetto ---
    game.process_action(PlayCardAction(test_card_flower))

    run_test(
        "Flower (Gioca dalla mano)",
        len(p1.hand) == 0,
        "Il fiore non è stato rimosso dalla mano"
    )
    run_test(
        "Flower (Appare in gioco)",
        len(p1.in_play_items) == 1 and p1.in_play_items[0].card == test_card_flower,
        "Il fiore non è apparso in 'in_play_items'"
    )

    # --- Test 2: Attivare l'abilità ---
    actions_flower = game.get_actions()
    flower_ability_action = next(
        (a for a in actions_flower if isinstance(a, TriggeredAbilityAction) and a.card == test_card_flower),
        None
    )
    run_test(
        "Flower (Abilità appare in get_actions)",
        flower_ability_action is not None,
        "L'abilità del fiore non è stata trovata"
    )
    
    # Attiviamo (questo tappa l'oggetto)
    game.process_action(flower_ability_action)

    run_test(
        "Flower (Entra in Fase Targeting)",
        game.phase == GamePhase.CHOOSE_TARGET,
        "Il gioco non è entrato in CHOOSE_TARGET"
    )

    # --- Test 3: Scegliere il bersaglio e curare ---
    target_actions_flower = game.get_actions()
    target_olaf_action_2 = next(
        (a for a in target_actions_flower if isinstance(a, AbilityTargetAction) and a.target_card == olaf),
        None
    )
    run_test(
        "Flower (Trova bersaglio valido)",
        target_olaf_action_2 is not None,
        "Non è stata trovata l'azione per bersagliare Olaf"
    )
    
    # Applichiamo (questo cura e poi banisha)
    game.process_action(target_olaf_action_2)

    run_test(
        "Flower (Effetto applicato - Cura)",
        char_to_heal_2.damage == 1, # Cura 3 (da 4 a 1)
        f"Olaf dovrebbe avere 1 danno, ne ha {char_to_heal_2.damage}"
    )
    run_test(
        "Flower (Ritorna in Fase MAIN)",
        game.phase == GamePhase.MAIN,
        "Il gioco non è tornato in Fase MAIN"
    )

    # --- Test 4: Verificare il Banish (post-cura) ---
    run_test(
        "Flower (Oggetto Rimosso/Banish)",
        len(p1.in_play_items) == 0, # L'item è stato banishato
        "L'oggetto non è stato rimosso da in_play_items dopo il banish"
    )
    run_test(
        "Flower (Oggetto in discard)",
        test_card_flower in p1.discard, #
        "L'oggetto non è finito negli scarti dopo il banish"
    )
    
    # --- Test 5: L'abilità non è disponibile (perché l'item non esiste) ---
    actions_after_use_flower = game.get_actions()
    item_ability_action_after_flower = next(
        (a for a in actions_after_use_flower if isinstance(a, TriggeredAbilityAction) and a.card == test_card_flower),
        None
    )
    run_test(
        "Flower (Abilità non disponibile post-banish)",
        item_ability_action_after_flower is None,
        "L'abilità dell'oggetto è ancora disponibile anche se banishato"
    )


    print("\n--- Tutti i test sugli Oggetti Attivabili sono stati superati! ---")