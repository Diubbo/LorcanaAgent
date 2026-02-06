import unittest
import sys
sys.path.insert(1, '/Users/diub/PycharmProjects/lorcanaAiProject/lorcana')
from game_enums import GamePhase
from lorcana.contestant import Contestant
from controller import  EnvironmentController, RandomController
from RuleBasedController import RuleBasedController
from decklists import amber_amethyst, sapphire_steel

from game import Game
from state_extractor import extract_game_state

class TestHeuristicMatch(unittest.TestCase):

    def play_match(self, controller1, controller2, max_turns=150):
        c1 = Contestant( sapphire_steel, controller1)
        c2 = Contestant( amber_amethyst, controller2)

        game = Game(c1, c2, EnvironmentController())
        for t in range(max_turns):
           
            if game.phase == GamePhase.GAME_OVER :
                break
            actions = game.get_actions()
            if not actions:
                game.swap_current_player()
                continue

            state = extract_game_state(game)
            action = game.currentController.chooseAction(actions, state)
            game.process_action(action)
        print("game over in turn", t)
        return game
    
    def test_simple_vs_random(self):
        rb_controller = RuleBasedController("PLAYER1", print_logs=False)
        rand_controller = RandomController("PLAYER2", print_logs=False)

        wins = {"PLAYER1": 0, "PLAYER2": 0}
        for _ in range(10):  # run multiple games
            game = self.play_match(rb_controller, rand_controller)
            if game.winner:
                wins[game.winner.name] += 1
                print("P1: ",game.p1.lore ," P2: ",game.p2.lore)
        print("Results Simple RB vs RNG:", wins)
        self.assertGreater(wins["PLAYER1"], wins["PLAYER2"])



if __name__ == "__main__":
    unittest.main()

    """
    def test_simple_vs_simple(self):
            rb1 = RuleBasedController("PLAYER1", print_logs=False)
            rb2 = RuleBasedController("PLAYER2", print_logs=False)

            wins = {"PLAYER1": 0, "PLAYER2": 0}
            for _ in range(10):
                
                game = self.play_match(rb1, rb2)
                if game.winner:
                    wins[game.winner.name] += 1
                    print("P1: ",game.p1.lore ," P2: ",game.p2.lore)

            print("Results RB1 vs RB2:", wins)
            self.assertTrue(sum(wins.values()) > 0)  # at least one winner
"""