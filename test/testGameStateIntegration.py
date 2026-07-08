import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from controller import RandomController
from RuleBasedController import RuleBasedController
from state_extractor import extract_game_state
from game import Game
from contestant import Contestant
from deck import Deck  # se serve per inizializzare un deck vuoto
from decklists import amber_amethyst,sapphire_steel
class TestGameStateIntegration(unittest.TestCase):

    def setUp(self):
        # init with 2 stock decks
        c1 = Contestant(amber_amethyst, RuleBasedController("AI", print_logs=False))
        c2 = Contestant(sapphire_steel, RandomController("Rand", print_logs=False))
        self.game = Game(c1, c2, RandomController("env"))

    def test_extract_game_state(self):
        state = extract_game_state(self.game)
        self.assertIsNotNone(state)
        self.assertEqual(state.currentPlayer.name, self.game.currentPlayer.controller.name)
        self.assertEqual(state.currentOpponent.name, self.game.currentOpponent.controller.name)
        print(f"Current Player: {state.currentPlayer.name}, Opponent: {state.currentOpponent.name}")

    def test_rulebased_uses_game_state(self):
        state = extract_game_state(self.game)
        actions = self.game.currentPlayer.get_ink_actions()
        print(f"Available Ink Actions: {actions}")
        if actions:  # se ci sono azioni inkabili
            action = self.game.currentController.chooseAction(actions, state)
            self.assertIn(action, actions)
            print(f"Chosen action: {action}")
        else:
            self.skipTest("Nessuna azione disponibile in questa fase")

if __name__ == "__main__":
    unittest.main()
