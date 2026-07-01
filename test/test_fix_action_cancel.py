#!/usr/bin/python3
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from game import Game
from game_enums import GamePhase, PlayerTurn
from contestant import Contestant
from controller import RandomController, EnvironmentController
from decklists import amber_amethyst, sapphire_steel, fire_the_cannons, smash
from action import PlayCardAction, PassAction


def make_main_game(card_in_hand, ink):
    """MAIN phase game for P1 with a single card in hand and no characters in play."""
    c1 = Contestant(amber_amethyst, RandomController('p1'))
    c2 = Contestant(sapphire_steel, RandomController('p2'))
    game = Game(c1, c2, EnvironmentController())
    game.phase = GamePhase.MAIN
    game.player = PlayerTurn.PLAYER1
    game.currentPlayer = game.p1
    game.currentOpponent = game.p2
    game.p1.hand = [card_in_hand]
    game.p1.ready_ink = ink
    return game


class TestTargetedActionCardCancelOnNoTargets(unittest.TestCase):
    """Targeted ActionCards played when no valid targets exist must be
    discarded (not leaked) when the only available action is PassAction."""

    def test_playing_targeted_card_enters_choose_target(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        self.assertEqual(GamePhase.CHOOSE_TARGET, game.phase)

    def test_only_pass_offered_when_no_characters_exist(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        actions = game.get_actions()
        self.assertEqual(1, len(actions))
        self.assertIsInstance(actions[0], PassAction)

    def test_card_is_in_discard_after_cancel(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertIn(fire_the_cannons, game.p1.discard)

    def test_card_is_not_in_hand_after_cancel(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertNotIn(fire_the_cannons, game.p1.hand)

    def test_phase_returns_to_main_after_cancel(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertEqual(GamePhase.MAIN, game.phase)

    def test_pending_ability_cleared_after_cancel(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertIsNone(game.pending_ability)

    def test_pending_ability_card_cleared_after_cancel(self):
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertIsNone(game.pending_ability_card)

    def test_ink_is_spent_even_on_cancel(self):
        # card was already played — ink cost is non-refundable
        game = make_main_game(fire_the_cannons, 3)
        game.process_action(PlayCardAction(fire_the_cannons))
        game.process_action(PassAction())
        self.assertEqual(2, game.p1.ready_ink)  # 3 - cost(1) = 2

    def test_works_for_other_targeted_action_cards(self):
        # smash costs 3 and also has DamageTriggeredAbility
        game = make_main_game(smash, 5)
        game.process_action(PlayCardAction(smash))
        self.assertEqual(GamePhase.CHOOSE_TARGET, game.phase)
        game.process_action(PassAction())
        self.assertIn(smash, game.p1.discard)
        self.assertEqual(GamePhase.MAIN, game.phase)


if __name__ == '__main__':
    unittest.main()
