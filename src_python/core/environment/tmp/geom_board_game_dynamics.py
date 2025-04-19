import numpy as np
from src_python.core.environment.action_set_geom_board import ActionSet
from typing import Tuple, List
import hashlib
import zlib
import pickle

class GameDynamics:
    def __init__(self, board_size, start_state, goal_state):
        self.board_size = board_size
        self.state = start_state.copy()
        self.goal_state = goal_state.copy()
        self.num_objects = start_state.shape[0]

    def is_legal(self, new_state):
        """Check if the new checkpoint_state is legal."""
        positions = set()
        for obj in new_state:
            x, y = int(obj[1]), int(obj[2])
            if (x, y) in positions or not (0 <= x < self.board_size and 0 <= y < self.board_size):
                return False
            positions.add((x, y))
        return True

    def apply_action(self, action, *args):
        """Apply an action to the board checkpoint_state and return (action_was_legal, game_is_done)."""
        new_state = action(self.state.copy(), *args)
        is_legal = self.is_legal(new_state)
        if is_legal:
            self.state = new_state
        return is_legal, self.is_done()

    def is_done(self):
        """Check if the game is complete by comparing current and goal states."""
        return np.array_equal(self.state[:, 1:3], self.goal_state[:, 1:3])

    def get_state(self):
        """Return the current board checkpoint_state."""
        return self.state

    #-------------------------------#
    #       Static Methods
    #-------------------------------#
    # TODO: evaluate which compression method is best
    @staticmethod
    def compress_state(start_state: List[Tuple[int, int]], goal_state: List[Tuple[int, int]]) -> bytes:
        """Compress the checkpoint_state with zlib"""
        state_data = pickle.dumps((start_state, goal_state))
        compressed_state = zlib.compress(state_data)
        return compressed_state

    @staticmethod
    def state_to_md5(start_state: str, goal_state: str) -> str:
        """Create an MD5 hash from the states."""
        state_str = ','.join(map(str, start_state + goal_state))
        return hashlib.md5(state_str.encode()).hexdigest()

    @staticmethod
    def compress_with_zlib(start_state: List[Tuple[int, int]], goal_state: List[Tuple[int, int]]) -> bytes:
        """Compress the checkpoint_state combination using zlib."""
        state_combination = (tuple(map(tuple, start_state)), tuple(map(tuple, goal_state)))
        state_str = str(state_combination)  # Convert the checkpoint_state tuple to a string
        return zlib.compress(state_str.encode())  # Compress the encoded string and return bytes


if __name__ == "__main__":
    # Example usage:
    board_size = 5
    start_state = np.array([[0, 1, 1, 0, 0], [1, 2, 2, 0, 0]])  # [id, x, y, orientation, extra]
    goal_state = np.array([[0, 3, 3, 0, 0], [1, 1, 1, 0, 0]])
    game = GameDynamics(board_size, start_state, goal_state)

    print("Initial State:")
    print(game.get_state())

    action_legal, game_done = game.apply_action(ActionSet.move, 0, 1, 1)
    print("After Move:", action_legal, game_done)
    print(game.get_state())

    action_legal, game_done = game.apply_action(ActionSet.flip, 1)
    print("After Flip:", action_legal, game_done)
    print(game.get_state())

    action_legal, game_done = game.apply_action(ActionSet.addrmv, 0, 4, 1)
    print("After Addrmv:", action_legal, game_done)
    print(game.get_state())

    action_legal, game_done = game.apply_action(ActionSet.rotate, 1, 'top-left')
    print("After Rotate:", action_legal, game_done)
    print(game.get_state())
