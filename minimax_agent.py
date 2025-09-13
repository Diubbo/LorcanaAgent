# minimax_agent.py
class MinimaxAgent:
    def __init__(self, depth=2, eval_fn=None):
        self.depth = depth
        self.eval_fn = eval_fn or (lambda state, player: state.engine.currentPlayer.lore)

    def step(self, state):
        actions = state.legal_actions()
        if not actions:
            return None
        best_action, _ = self.minimax(state, self.depth, state.current_player())
        return best_action

    def minimax(self, state, depth, player):
        if depth == 0 or state.is_terminal():
            return None, self.eval_fn(state, player)

        best_score = float("-inf") if state.current_player() == player else float("inf")
        best_action = None

        for action in state.legal_actions():
            child = state.clone()
            child.apply_action(action)
            _, score = self.minimax(child, depth - 1, player)

            if state.current_player() == player:
                if score > best_score:
                    best_score, best_action = score, action
            else:
                if score < best_score:
                    best_score, best_action = score, action

        return best_action, best_score
