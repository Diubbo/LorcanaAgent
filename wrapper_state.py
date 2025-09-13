from game_enums import GamePhase, PlayerTurn
from contestant import Contestant
from action import AbilityTargetAction, DrawAction, FirstPlayerAction, PassAction
import pyspiel
from controller import EnvironmentController
from RuleBasedController import RuleBasedController
from game import Game

class LorcanaState(pyspiel.State):
    def __init__(self, game, deck1, deck2):
        super().__init__(game)
        self.engine = Game(Contestant( deck1, RuleBasedController("Player1") ), Contestant( deck2, RuleBasedController("Player2") ), EnvironmentController())  
        self.deck1 = deck1
        self.deck2 = deck2
        self._is_chance = False


    def current_player(self) -> int:
        if self.engine.phase == GamePhase.GAME_OVER:
            return pyspiel.PlayerId.TERMINAL
        return 0 if self.engine.player == PlayerTurn.PLAYER1 else 1

    def legal_actions(self, player: int = None) -> list[int]:
        actions = self.engine.get_actions()
        if not actions and not self.is_terminal():


        # fallback 
            return [0]
        result = list(range(len(actions)))
        return list(range(len(actions)))


    def apply_action(self, action: int) -> None:
        actions = self.engine.get_actions()
        if not actions:
            # fallback based on game phase
            if self.engine.phase == GamePhase.DIE_ROLL:
                # forces FirstPlayerAction to choose who starts
                self.engine.process_action(FirstPlayerAction(False))
            elif self.engine.phase == GamePhase.MULLIGAN:
                self.engine.process_action(PassAction())
            elif self.engine.phase == GamePhase.DRAW_STARTING_HAND:
                card_choices = self.engine.currentPlayer.get_top_card_choices()
                if card_choices:
                    card, qty = next(iter(card_choices.items()))
                    self.engine.process_action(DrawAction(card, qty))
                else:
                    self.engine.process_action(PassAction())
            
            else:
                # generico Pass
                self.engine.process_action(PassAction())
            return
        chosen_action = actions[action]
        self.engine.process_action(chosen_action)

    def is_terminal(self) -> bool:
        return self.engine.phase == GamePhase.GAME_OVER

    def is_chance_node(self) -> bool:
        return self._is_chance
    # returns adapt for pyspiel logic
    def returns(self) -> list[float]:
        if not self.is_terminal():
            return [0.0, 0.0]
        return [1.0, -1.0] if self.engine.winner == PlayerTurn.PLAYER1 else [-1.0, 1.0]

    def action_to_string(self, player, action):
        # index to action mapping
        actions = self.engine.get_actions()
        if 0 <= action < len(actions):
            return f"{actions[action]}"
        return f"Invalid action {action}"



class LorcanaGame(pyspiel.Game):
    def __init__(self, deck1, deck2):
        game_type = pyspiel.GameType(
            short_name="lorcana",
            long_name="Disney Lorcana",
            dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
            chance_mode=pyspiel.GameType.ChanceMode.SAMPLED_STOCHASTIC,
            information=pyspiel.GameType.Information.IMPERFECT_INFORMATION,
            utility=pyspiel.GameType.Utility.ZERO_SUM,
            reward_model=pyspiel.GameType.RewardModel.TERMINAL,
            max_num_players=2,
            min_num_players=2,
            provides_information_state_string=True,
            provides_information_state_tensor=False,
            provides_observation_string=True,
            provides_observation_tensor=False,
        )

        game_info = pyspiel.GameInfo(
            num_distinct_actions=200,
            max_chance_outcomes=0,
            num_players=2,
            min_utility=-1.0,
            max_utility=1.0,
            utility_sum=0.0,
            max_game_length=200,
        )

        super().__init__(game_type, game_info, {})

        self.deck1 = deck1
        self.deck2 = deck2

    def new_initial_state(self):
        return LorcanaState(self, self.deck1, self.deck2)

