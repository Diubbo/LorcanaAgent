from open_spiel.python.algorithms import mcts
import numpy as np

class RandomRolloutAgent:
    def __init__(self, game, rollout_count=5, seed=42):
        self.evaluator = mcts.RandomRolloutEvaluator(rollout_count)
        self.rng = np.random.RandomState(seed)
        self.game = game

    def step(self, state):
        actions = state.legal_actions()
        if not actions:
            return None

        scores = []
        for action in actions:
            child = state.clone()
            child.apply_action(action)
            result = self.evaluator.evaluate(child)
            scores.append(result[state.current_player()])

        # Sceglie l’azione col punteggio medio migliore
        best_idx = int(np.argmax(scores))
        return actions[best_idx]
