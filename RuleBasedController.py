from controller import Controller
import heuristic  

class RuleBasedController(Controller):
    def __init__(self, name, print_logs=False):
        super().__init__(name, print_logs)

    def chooseAction(self, actions, gamestate):
        # Se esiste engine → siamo nel wrapper LorcanaState (OpenSpiel)
        if hasattr(gamestate, "engine"):
            real_actions = gamestate.engine.get_actions()
            idx_mode = True
        else:
            # Vecchio stile → le actions passate sono già reali
            real_actions = actions
            idx_mode = False

        best_idx = None
        best_score = float("-inf")
        best_fn = None

        for fn in [
                    heuristic.mulligan_heuristic, #
                    heuristic.ink_heuristic, #
                    
                    # Euristiche per GIOCARE CARTE (in competizione tra loro)
                    heuristic.play_character_heuristic,
                    heuristic.play_draw_card_action_heuristic,
                    heuristic.play_ramp_action_heuristic,
                    heuristic.play_target_damage_action_heuristic,
                    heuristic.play_aoe_damage_action_heuristic,
                    heuristic.play_aoe_heal_action_heuristic,
                    heuristic.play_target_heal_action_heuristic,
                    heuristic.play_banish_item_action_heuristic,
                    heuristic.play_item_heuristic, #
                    
                    # Euristiche per AZIONI SUL CAMPO
                    heuristic.quest_heuristic, #
                    heuristic.deny_lore_heuristic, #
                    heuristic.tempo_push_heuristic, #
                    heuristic.challenge_efficiency_heuristic, #
                    
                    # Euristiche per ABILITÀ ATTIVABILI
                    heuristic.healing_ability_heuristic, #
                    heuristic.damage_ability_heuristic, #
                    
                    # Fallback
                    heuristic.endturn_heuristic, #
        ]:
            idx, score = fn(actions, gamestate)

            if idx is None:
                continue

            if score > best_score:
                best_idx, best_score = idx, score
                best_fn = fn.__name__

        if best_idx is not None:
            chosen = real_actions[best_idx] if idx_mode else best_idx  # in old style l’euristica restituisce l’azione stessa
            if self.print_logs:
                print(f"[Heuristic] {best_fn} -> {chosen} (score={best_score})")
            return chosen

        # fallback
        if self.print_logs:
            print("[Fallback] No heuristic matched, choosing first action")
        return real_actions[0] if real_actions else None
