import numpy as np
from src_python.core.environment.action_set_geom_board import ActionSetGeomBoard
from typing import Tuple, List, Dict, Hashable
from .game_system import GameSystem

def validate_action_output(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if self.is_valid_state(result):
            return result
        return args[0].copy()  # fallback to original board_state

    return wrapper

class GameSystemGeomBoard(GameSystem):

    def __init__(self, board_width: int, board_height: int, action_set: Dict[str, bool]):
        self.board_width = board_width
        self.board_height = board_height
        self.board_size = board_width * board_height
        self.action_set = action_set
        self.actions = ActionSetGeomBoard()

    # -------------------------------
    # Core ActionModel Application
    # -------------------------------
    def apply_action(self, board_state: dict, action_type: str) -> dict:
        """ Returns a new board checkpoint_state after applying the given action. """
        new_state = self.deep_copy_state(board_state)

        if hasattr(self.actions, action_type):
            action_method = getattr(self.actions, action_type)
            return action_method(new_state)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def apply_immediate_action(self, board_state: dict, action_type: str) -> dict:
        """ Applies 'immediate' actions like flip, add, rmv. """
        new_state = self.deep_copy_state(board_state)

        if hasattr(self.actions, action_type):
            action_method = getattr(self.actions, action_type)
            if action_type == "add":
                return action_method(new_state, self.board_width, self.board_height)
            else:
                return action_method(new_state)
        else:
            raise ValueError(f"Unknown immediate action type: {action_type}")

    def is_valid_state(self, board_state: np.ndarray) -> bool:
        positions = board_state[:, 0]
        stack_levels = board_state[:, 1]
        orientations = board_state[:, 2]

        # All positions on-board must be in the valid range (1–board_size²)
        if not np.all(np.isin(positions[stack_levels >= 0], range(1, self.board_size ** 2 + 1))):
            return False

        # All on-board orientations must be valid (1–12)
        if not np.all((orientations[stack_levels >= 0] >= 1) & (orientations[stack_levels >= 0] <= 12)):
            return False

        # Optional: prevent duplicate (position, stack_level) combinations
        # if needed — otherwise allow stacking
        pos_stack_pairs = set(tuple(x[:2]) for x in board_state if x[1] >= 0)
        if len(pos_stack_pairs) != np.sum(board_state[:, 1] >= 0):
            return False

        return True

    @validate_action_output
    def apply_action_randomly(self, board_state: np.ndarray, action_type: str) -> np.ndarray:
        if not hasattr(self.actions, action_type):
            raise ValueError(f"Unknown action type: {action_type}")

        object_index = np.random.randint(0, board_state.shape[0]) if board_state.shape[0] > 0 else 0
        direction = np.random.choice(["up", "down", "left", "right"])
        print(f'action is: {action_type}, {object_index}, {direction}')
        return getattr(self.actions, action_type)(
            board_state=board_state.copy(),
            object_index= object_index,
            direction=direction
        )

    # -------------------------------
    # A* Support Methods
    # -------------------------------
    def get_legal_actions(self, board_state: dict) -> List[str]:
        """ Returns all legal actions from this checkpoint_state. """
        return [action for action, enabled in self.action_set.items() if enabled]

    def heuristic(self, board_state: dict, goal_state: dict) -> float:
        """ Example heuristic — count number of mismatched cells (or geoms). """
        return sum(1 for k, v in board_state.items() if v != goal_state.get(k))


