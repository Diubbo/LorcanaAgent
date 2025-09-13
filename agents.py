# agents.py
from open_spiel.python.algorithms import mcts
import numpy as np
from heuristic_eval import HeuristicEvaluator
from minimax_agent import MinimaxAgent
from random_rollout_agent import RandomRolloutAgent
from open_spiel.python.algorithms import cfr

def make_agent(agent_type, game, seed=42):
    if agent_type == "mcts":
        eval_fn = HeuristicEvaluator() 
        return mcts.MCTSBot(
            game=game,
            uct_c=1.0,
            max_simulations=100,
            evaluator=eval_fn,
            solve=True,
            random_state=np.random.RandomState(seed)
        )
    elif agent_type == "minimax":
        return MinimaxAgent(depth=2)   
    elif agent_type == "random":
        return RandomRolloutAgent(game, rollout_count=10, seed=seed)

    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
