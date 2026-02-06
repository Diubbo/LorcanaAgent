# minimax_agent.py
class MinimaxAgent:
    def __init__(self, depth=2, eval_fn=None): 
        self.depth = depth
        # self.eval_fn = eval_fn or your_wrapped_combined_heuristic
        self.eval_fn = eval_fn or (lambda state, player: state.engine.currentPlayer.lore) 

    def step(self, state):
        actions = state.legal_actions()
        if not actions:
            return None
        
        # --- Call alpha_beta ---
        # Start with initial alpha=-inf and beta=+inf
        best_action, _ = self.alpha_beta(state, self.depth, float("-inf"), float("inf"), state.current_player())
        
        # Fallback if no action found (shouldn't happen if legal_actions is not empty)
        return best_action if best_action is not None else actions[0]


    def alpha_beta(self, state, depth, alpha, beta, player):
        """
        Minimax search with Alpha-Beta Pruning.
        Args:
            state: The current game state (must implement clone, apply_action, etc.).
            depth: Remaining search depth.
            alpha: Best score guaranteed for the maximizing player.
            beta: Best score guaranteed for the minimizing player.
            player: The original player ID whose score we are maximizing/minimizing relative to.
        Returns:
            A tuple (best_action, best_score).
        """
        if depth == 0 or state.is_terminal():
            # Evaluate from the perspective of the original player
            score = self.eval_fn(state, player) 
            # Adjust score perspective if needed (if eval_fn doesn't handle it)
            return None, score

        is_maximizing_player = (state.current_player() == player)
        best_score = float("-inf") if is_maximizing_player else float("inf")
        best_action = None
        
        legal_actions = state.legal_actions()
        # If no legal actions, return evaluation of current state
        if not legal_actions:
             score = self.eval_fn(state, player)
             return None, score

        # Ensure there's always a default action if all branches get pruned weirdly
        best_action = legal_actions[0] 

        for action in legal_actions:
            child = state.clone()
            child.apply_action(action)
            # Recursive call, passing down alpha and beta
            _, score = self.alpha_beta(child, depth - 1, alpha, beta, player)

            if is_maximizing_player:
                if score > best_score:
                    best_score = score
                    best_action = action
                # Update alpha
                alpha = max(alpha, best_score)
                # Beta Pruning check
                if beta <= alpha:
                    break # Stop searching this node's children
            else: # Minimizing player
                if score < best_score:
                    best_score = score
                    best_action = action
                # Update beta
                beta = min(beta, best_score)
                # Alpha Pruning check
                if beta <= alpha:
                    break # Stop searching this node's children

        return best_action, best_score