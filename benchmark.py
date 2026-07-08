import time
import random
import numpy as np
import pyspiel

# --- Project Imports ---
# Core Game/State
from wrapper_state import LorcanaGame
from decklists import amber_amethyst, sapphire_steel 

# Agent Creation & Heuristics
from agents import make_agent # Central function for agent creation

# --- Configuration ---
NUM_MATCHES = 5 # Number of games per matchup (adjust as needed)
AGENT_TYPES = ["mcts", "minimax", "rulebased", "random"] # Agents to test
DECK1 = sapphire_steel # Deck for Player 0
DECK2 = sapphire_steel # Deck for Player 1

# --- Helper Function to Create Agents ---

def create_specific_agent(agent_type_str, game):
    """Creates an agent instance based on the type string, using make_agent where possible."""
    seed = random.randint(0, 1000000)

    # Use make_agent for standard agent types
    if agent_type_str in ["mcts", "minimax", "random", "rulebased"]:
         # Uses the parameters defined within make_agent (e.g., simulations, depth)
         return make_agent(agent_type_str, game, seed=seed) #

    else:
        raise ValueError(f"Unknown agent type for benchmark: {agent_type_str}")

# --- Simulation Function ---

def play_match(game, agent1, agent2):
    """Simulates a single match and returns the winner (0 or 1, or -1 for draw)."""
    state = game.new_initial_state()
    agents = [agent1, agent2]

    while not state.is_terminal():
        player_id = state.current_player()
        # Skip chance nodes if they ever appear (unlikely in current setup)
        if player_id < 0:
             outcome = random.choice(state.chance_outcomes())
             state.apply_action(outcome)
             continue

        current_agent = agents[player_id]
        action = current_agent.step(state) # All agents use step(state) now
        state.apply_action(action)

    returns = state.returns()
    if returns[0] > returns[1]: return 0 # Player 0 wins
    elif returns[1] > returns[0]: return 1 # Player 1 wins
    else: return -1 # Draw

# --- Benchmark Runner ---

def run_benchmark(game, agent1_type, agent2_type, num_matches):
    """Runs N matches between two agent types and prints results."""
    print(f"\n--- Benchmarking: {agent1_type} (P0) vs {agent2_type} (P1) [{num_matches} matches] ---")
    start_time = time.time()
    wins = {0: 0, 1: 0, -1: 0} # P0 wins, P1 wins, Draws

    for i in range(num_matches):
        # Create fresh agents with new seeds for each match
        agent1 = create_specific_agent(agent1_type, game)
        agent2 = create_specific_agent(agent2_type, game)

        winner = play_match(game, agent1, agent2)
        wins[winner] += 1
        # Simple progress indicator
        print(f"  Match {i+1}/{num_matches} complete.", end='\r')

    end_time = time.time()
    total_time = end_time - start_time
    matches_per_sec = num_matches / total_time if total_time > 0 else float('inf')

    # Calculate win rates
    win_rate_p0 = (wins[0] / num_matches) * 100 if num_matches > 0 else 0
    win_rate_p1 = (wins[1] / num_matches) * 100 if num_matches > 0 else 0
    draw_rate = (wins[-1] / num_matches) * 100 if num_matches > 0 else 0

    # Print results clearly
    print("\n" + "="*50)
    print(f"  Results for {agent1_type} (P0) vs {agent2_type} (P1):")
    print(f"    {agent1_type} Wins:    {wins[0]:>5} ({win_rate_p0:>5.1f}%)")
    print(f"    {agent2_type} Wins:    {wins[1]:>5} ({win_rate_p1:>5.1f}%)")
    if wins[-1] > 0:
        print(f"    Draws:        {wins[-1]:>5} ({draw_rate:>5.1f}%)")
    print(f"  Total time: {total_time:.2f} seconds ({matches_per_sec:.2f} matches/sec)")
    print("="*50)

    # Return results for summary
    return {
        "P0_Agent": agent1_type,
        "P1_Agent": agent2_type,
        "P0_Wins": wins[0],
        "P1_Wins": wins[1],
        "Draws": wins[-1],
        "P0_WinRate": win_rate_p0,
        "P1_WinRate": win_rate_p1,
    }

# --- Main Benchmark Execution ---
if __name__ == "__main__":
    try:
        from heuristic_eval import HeuristicEvaluator
        from open_spiel.python.algorithms import mcts
    except ImportError as e:
        print(f"Warning: Could not import MCTS dependencies - {e}")


    print("Initializing Lorcana Game for Benchmark...")
    lorcana_game = LorcanaGame(DECK1, DECK2)

    # Define matchups to run (Player 0 type vs Player 1 type)
    matchups_to_run = [
        #("mcts", "random"),
        #("minimax", "random"),
        ("mcts", "minimax"),
    ]

    all_results_summary = []

    print(f"\nStarting Benchmarks ({NUM_MATCHES} matches per matchup)...")
    overall_start_time = time.time()

    for p0_agent_type, p1_agent_type in matchups_to_run:
        match_result = run_benchmark(lorcana_game, p0_agent_type, p1_agent_type, NUM_MATCHES)
        all_results_summary.append(match_result)

    overall_end_time = time.time()
    print(f"\n--- Benchmark Finished ---")
    print(f"Total Benchmark Duration: {overall_end_time - overall_start_time:.2f} seconds")

    print("\n--- Summary Table ---")
    print("P0 Agent      | P1 Agent      | P0 Wins (%)  | P1 Wins (%)  | Draws")
    print("--------------|---------------|--------------|--------------|-------")
    for res in all_results_summary:
        print(f"{res['P0_Agent']:<13} | {res['P1_Agent']:<13} | "
              f"{res['P0_Wins']:>3} ({res['P0_WinRate']:>5.1f}%) | "
              f"{res['P1_Wins']:>3} ({res['P1_WinRate']:>5.1f}%) | "
              f"{res['Draws']:>5}")
    print("--------------|---------------|--------------|--------------|-------")