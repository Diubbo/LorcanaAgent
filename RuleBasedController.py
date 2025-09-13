from controller import Controller
import heuristic  

class RuleBasedController(Controller):
    def __init__(self, name, print_logs=False):
        super().__init__(name, print_logs)

    def chooseAction(self, actions, gamestate):
        best_action = None
        best_score = float("-inf")

        for fn in [
            heuristic.mulligan_heuristic,
            heuristic.ink_heuristic,
            heuristic.play_heuristic,
            heuristic.quest_heuristic,
            heuristic.deny_lore_heuristic,
            heuristic.tempo_push_heuristic,
            heuristic.challenge_efficiency_heuristic,
            heuristic.endturn_heuristic,   
        ]:
            action, score = fn(actions, gamestate)
            if action and score > best_score:
                best_action, best_score = action, score
                if self.print_logs:
                    print(f"[Heuristic] {fn.__name__} -> {action} (score={score})")

        if best_action:
            return best_action

        # fallback
        if self.print_logs:
            print("[Fallback] No heuristic matched, choosing first action")
        return actions[0]
