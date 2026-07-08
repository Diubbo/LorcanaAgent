from game import Game
from game_enums import GamePhase
from contestant import Contestant
from controller import EnvironmentController

class LorcanaEnv:
    def __init__(self, controller1, controller2, deck1, deck2):
        self.controller1 = controller1
        self.controller2 = controller2
        self.deck1 = deck1
        self.deck2 = deck2

    def reset(self):
        self.game = Game(
            Contestant(self.deck1, self.controller1),
            Contestant(self.deck2, self.controller2),
            EnvironmentController(),
        )
        return self._get_obs()

    def step(self, action):
        self.game.process_action(action)
        done = self.game.phase == GamePhase.GAME_OVER
        reward = 0
        if done:
            reward = 1 if self.game.winner == self.game.player else -1
        return self._get_obs(), reward, done, {"winner": self.game.winner if done else None}

    def legal_actions(self):
        return self.game.get_actions()

    def _get_obs(self):
        # key features from the game state
        return {
            "phase": self.game.phase,
            "p1_lore": self.game.p1.lore,
            "p2_lore": self.game.p2.lore,
            "p1_hand": len(self.game.p1.hand),
            "p2_hand": len(self.game.p2.hand),
        }
