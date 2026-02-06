from open_spiel.python.algorithms.async_mcts import Evaluator
import numpy as np
from heuristic import combined_heuristic, static_state_evaluation_heuristic

class HeuristicEvaluator(Evaluator):
    def __init__(self):
        self.heuristic_fn = combined_heuristic
        self.state_evaluation_fn = static_state_evaluation_heuristic

    def evaluate(self, state):
        player = state.current_player()
        raw_score = self.state_evaluation_fn(state, player)
        return [raw_score if p == player else -raw_score for p in range(state.num_players())]

    def prior(self, state):
        actions = list(state.legal_actions())
        if not actions:
            return []
        original_player = state.current_player()
        scores = []
        # Evaluate each action
        for a in actions:
            next_state = state.clone()
            next_state.apply_action(a)
            score = self.heuristic_fn(next_state, next_state.current_player())

            if next_state.current_player() != original_player:
                score = -score

            scores.append(score)
        # Shift scores to be positive
        min_score = min(scores) if scores else 0.
        positive_scores = [(s - min_score) + 0.01 for s in scores]

        # Normalize
        probs = np.array(positive_scores, dtype=float)
        probs_sum = probs.sum()
        
        if probs_sum > 0 and not np.isnan(probs_sum):
            probs /= probs_sum
        else:
            probs = np.ones(len(actions), dtype=float) / len(actions)        

        return list(zip(actions, probs))

    