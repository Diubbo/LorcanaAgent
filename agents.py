# agents.py
from open_spiel.python.algorithms import mcts
import numpy as np
from heuristic_eval import HeuristicEvaluator
from minimax_agent import MinimaxAgent
from heuristic import combined_heuristic, static_state_evaluation_heuristic

class UniformRandomAgent:
    def __init__(self, seed=None):
        self.rng = np.random.RandomState(seed)

    def step(self, state):
        legal_actions = state.legal_actions()
        if not legal_actions:
            return 0 
        
        # Sceglie un indice a caso dalla lista di azioni legali
        action_index = self.rng.choice(legal_actions)
        return action_index
    
def minimax_eval_wrapper(state, player_id):
    score = static_state_evaluation_heuristic(state, player_id)
    return score

def make_agent(agent_type, game, seed=42):
    if agent_type == "mcts":
        eval_fn = HeuristicEvaluator() 
        return mcts.MCTSBot(
            game=game,
            uct_c=1.0,
            max_simulations=200,
            evaluator= eval_fn, #mcts.RandomRolloutEvaluator(n_rollouts=5),
            solve=True,
            random_state=np.random.RandomState(seed)
        )
    elif agent_type == "minimax":
        return MinimaxAgent(depth=2, eval_fn=minimax_eval_wrapper)
    elif agent_type == "random":
        return UniformRandomAgent(seed=seed)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
