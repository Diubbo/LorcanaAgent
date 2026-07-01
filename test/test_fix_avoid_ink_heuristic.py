#!/usr/bin/python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from game import Game
from game_enums import GamePhase, PlayerTurn
from contestant import Contestant
from controller import RandomController, EnvironmentController
from decklists import amber_amethyst, sapphire_steel, olaf, jetsam, kristoff, hades
from action import InkAction
from heuristic import avoid_ink_evasion_heuristic


class FakeState:
    """Minimal wrapper giving heuristics access to state.engine."""
    def __init__(self, game):
        self.engine = game


def make_main_game(hand):
    c1 = Contestant(amber_amethyst, RandomController('p1'))
    c2 = Contestant(sapphire_steel, RandomController('p2'))
    game = Game(c1, c2, EnvironmentController())
    game.phase = GamePhase.MAIN
    game.player = PlayerTurn.PLAYER1
    game.currentPlayer = game.p1
    game.currentOpponent = game.p2
    game.p1.hand = list(hand)
    game.p1.ready_ink = 10
    return game


class TestAvoidInkEvasionHeuristic(unittest.TestCase):

    def _chosen_card(self, hand):
        game = make_main_game(hand)
        state = FakeState(game)
        actions = list(range(len(game.get_actions())))
        idx, _ = avoid_ink_evasion_heuristic(actions, state)
        return game.get_actions()[idx].card

    def test_prefers_to_ink_non_evasive_over_evasive(self):
        # jetsam has ("Evasive",) in keywords; olaf has tuple()
        chosen = self._chosen_card([olaf, jetsam])
        self.assertEqual(olaf, chosen)

    def test_does_not_choose_evasive_card_to_ink(self):
        chosen = self._chosen_card([olaf, jetsam])
        self.assertNotEqual(jetsam, chosen)

    def test_among_non_evasive_prefers_lower_lore(self):
        # olaf lore=1, kristoff lore=2 — both non-evasive
        chosen = self._chosen_card([olaf, kristoff])
        self.assertEqual(olaf, chosen)

    def test_returns_ink_action(self):
        game = make_main_game([olaf, jetsam])
        state = FakeState(game)
        actions = list(range(len(game.get_actions())))
        idx, _ = avoid_ink_evasion_heuristic(actions, state)
        self.assertIsInstance(game.get_actions()[idx], InkAction)

    def test_returns_none_index_when_no_inkable_cards(self):
        # hades is inkable=False so no InkActions are generated
        game = make_main_game([hades])
        state = FakeState(game)
        actions = list(range(len(game.get_actions())))
        result = avoid_ink_evasion_heuristic(actions, state)
        # function returns bare None when inks list is empty
        self.assertIsNone(result)

    def test_evasive_keyword_detection_is_case_sensitive(self):
        # "Evasive" (capital E) must match — verify jetsam is detected correctly
        self.assertIn("Evasive", jetsam.keywords)
        self.assertNotIn("Evasive", olaf.keywords)


if __name__ == '__main__':
    unittest.main()
