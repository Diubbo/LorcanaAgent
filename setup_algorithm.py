
import pyspiel
from wrapper_state import LorcanaGame
from decklists import amber_amethyst, sapphire_steel

from agents import make_agent
from wrapper_state import LorcanaGame
from decklists import amber_amethyst, sapphire_steel

lorcana_game = LorcanaGame(amber_amethyst, sapphire_steel)
# mcts minimax random at the moment
bot1 = make_agent("mcts", lorcana_game, seed=42)
bot2 = make_agent("minimax", lorcana_game, seed=43)
"""

state = lorcana_game.new_initial_state()
turn = 0

while not state.is_terminal():
    current_bot = bot1 if state.current_player() == 0 else bot2
    action = current_bot.step(state)
    action_str = state.action_to_string(state.current_player(), action)
    print(f"Player {state.current_player()} esegue: {action_str}")
    state.apply_action(action)

print("Returns:", state.returns())
"""
