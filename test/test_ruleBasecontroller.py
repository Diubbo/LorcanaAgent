import unittest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from controller import RandomController
from RuleBasedController import RuleBasedController
from state_extractor import extract_game_state
from game import Game, GamePhase
from contestant import Contestant
from deck import Deck
from decklists import amber_amethyst,sapphire_steel

class TestRuleBasedController(unittest.TestCase):

    def setUp(self):


        c1 = Contestant(amber_amethyst, RuleBasedController("AI", print_logs=False))
        c2 = Contestant(sapphire_steel, RandomController("Rand", print_logs=False))

        self.game = Game(c1, c2, RandomController("env"))

    def test_choose_action_with_game_state(self):
        # Otteniamo tutte le azioni disponibili dal Game
        actions = self.game.get_actions()
        state = extract_game_state(self.game)

        if actions:
            chosen = self.game.currentController.chooseAction(actions, state)
            self.assertIn(chosen, actions)  # deve essere una delle azioni lecite
        else:
            self.skipTest("Nessuna azione disponibile in questa fase")

    def test_full_auto_play(self):
        max_steps = 100
        steps = 0

        while self.game.phase != GamePhase.GAME_OVER and steps < max_steps:
            actions = self.game.get_actions()
            if not actions:
                break
            state = extract_game_state(self.game)
            action = self.game.currentController.chooseAction(actions, state)
            self.game.process_action(action)
            steps += 1

        # Il gioco deve essere coerente alla fine
        self.assertIn(self.game.phase, [GamePhase.MAIN, GamePhase.DRAW_PHASE,
                                        GamePhase.CHALLENGING, GamePhase.GAME_OVER])
        if self.game.phase == GamePhase.GAME_OVER:
            self.assertIn(self.game.winner.name, 
                          [self.game.p1.controller.name, self.game.p2.controller.name])
            print(f"Winner: {self.game.winner.name}")
if __name__ == "__main__":
    unittest.main()
