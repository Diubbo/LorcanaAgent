#!/usr/bin/python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from game import Game
from game_enums import GamePhase, PlayerTurn
from contestant import Contestant
from controller import RandomController, EnvironmentController
from decklists import amber_amethyst, sapphire_steel, olaf, flounder
from inplay_character import InPlayCharacter
from action import QuestAction, ChallengeAction


def make_main_game(p1_chars, p2_chars):
    """MAIN phase game with characters already in play.

    p1_chars: list of Card (all ready + dry)
    p2_chars: list of (Card, ready:bool)
    """
    c1 = Contestant(amber_amethyst, RandomController('p1'))
    c2 = Contestant(sapphire_steel, RandomController('p2'))
    game = Game(c1, c2, EnvironmentController())
    game.phase = GamePhase.MAIN
    game.player = PlayerTurn.PLAYER1
    game.currentPlayer = game.p1
    game.currentOpponent = game.p2
    for card in p1_chars:
        game.p1.in_play_characters.append(InPlayCharacter(card, dry=True, ready=True))
    for card, ready in p2_chars:
        game.p2.in_play_characters.append(InPlayCharacter(card, dry=True, ready=ready))
    return game


class TestDuplicateQuestActions(unittest.TestCase):

    def test_two_identical_olafs_produce_two_quest_actions(self):
        game = make_main_game([olaf, olaf], [])
        quest_actions = [a for a in game.get_actions()
                         if isinstance(a, QuestAction) and a.card == olaf]
        self.assertEqual(2, len(quest_actions))

    def test_quest_actions_have_different_indices(self):
        game = make_main_game([olaf, olaf], [])
        quest_actions = [a for a in game.get_actions()
                         if isinstance(a, QuestAction) and a.card == olaf]
        self.assertEqual({0, 1}, {a.index for a in quest_actions})

    def test_quest_with_index_0_exerts_first_character(self):
        game = make_main_game([olaf, olaf], [])
        game.process_action(QuestAction(olaf, 0))
        ready_states = [ch.ready for ch in game.p1.in_play_characters]
        self.assertIn(False, ready_states)
        self.assertIn(True, ready_states)

    def test_quest_with_index_1_exerts_second_character(self):
        game = make_main_game([olaf, olaf], [])
        game.process_action(QuestAction(olaf, 1))
        ready_states = [ch.ready for ch in game.p1.in_play_characters]
        self.assertIn(False, ready_states)
        self.assertIn(True, ready_states)

    def test_single_olaf_produces_one_quest_action(self):
        game = make_main_game([olaf], [])
        quest_actions = [a for a in game.get_actions()
                         if isinstance(a, QuestAction) and a.card == olaf]
        self.assertEqual(1, len(quest_actions))

    def test_both_olafs_can_quest_sequentially(self):
        game = make_main_game([olaf, olaf], [])
        game.process_action(QuestAction(olaf, 0))
        game.process_action(QuestAction(olaf, 1))
        ready_states = [ch.ready for ch in game.p1.in_play_characters]
        self.assertEqual([False, False], ready_states)


class TestDuplicateChallengeActions(unittest.TestCase):

    def test_two_identical_olafs_produce_two_challenge_actions(self):
        # flounder is exerted (ready=False) so it can be challenged
        game = make_main_game([olaf, olaf], [(flounder, False)])
        challenge_actions = [a for a in game.get_actions()
                             if isinstance(a, ChallengeAction) and a.card == olaf]
        self.assertEqual(2, len(challenge_actions))

    def test_challenge_actions_have_different_indices(self):
        game = make_main_game([olaf, olaf], [(flounder, False)])
        challenge_actions = [a for a in game.get_actions()
                             if isinstance(a, ChallengeAction) and a.card == olaf]
        self.assertEqual({0, 1}, {a.index for a in challenge_actions})

    def test_single_olaf_produces_one_challenge_action(self):
        game = make_main_game([olaf], [(flounder, False)])
        challenge_actions = [a for a in game.get_actions()
                             if isinstance(a, ChallengeAction) and a.card == olaf]
        self.assertEqual(1, len(challenge_actions))


if __name__ == '__main__':
    unittest.main()
