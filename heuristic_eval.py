from open_spiel.python.algorithms.async_mcts import Evaluator
import numpy as np
from heuristic import combined_heuristic

class HeuristicEvaluator(Evaluator):
    def __init__(self):
        self.heuristic_fn = combined_heuristic

    def evaluate(self, state):
        player = state.current_player()
        raw_score = self.heuristic_fn(state, player)
        return [raw_score if p == player else -raw_score for p in range(state.num_players())]

    def prior(self, state):
        actions = list(state.legal_actions())

        if not actions:
            return []

        scores = []
        for a in actions:
            # clone to simulate action
            next_state = state.clone()
            next_state.apply_action(a)

            # evaluate resulting state
            score = self.heuristic_fn(next_state, state.current_player())
            scores.append(max(score, 0.01))  # evita zeri

        # normalize scores to probabilities
        probs = np.array(scores, dtype=float)
        probs /= probs.sum()

        # return list of (action, probability) pairs
        return list(zip(actions, probs))
