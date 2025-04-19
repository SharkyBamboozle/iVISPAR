import numpy as np

FLIP_TRANSITIONS = {
    1: {"left": 8, "right": 12, "up": 9, "down": 5},
    2: {"left": 6, "right": 10, "up": 5, "down": 9},
    3: {"left": 10, "right": 6, "up": 7, "down": 11},
    4: {"left": 12, "right": 8, "up": 11, "down": 7},
    5: {"left": 7, "right": 9, "up": 1, "down": 2},
    6: {"left": 3, "right": 2, "up": 8, "down": 10},
    7: {"left": 11, "right": 5, "up": 4, "down": 3},
    8: {"left": 4, "right": 1, "up": 12, "down": 6},
    9: {"left": 5, "right": 11, "up": 2, "down": 1},
    10: {"left": 2, "right": 3, "up": 6, "down": 12},
    11: {"left": 9, "right": 7, "up": 3, "down": 4},
    12: {"left": 1, "right": 4, "up": 10, "down": 8},
}


def pos_to_coord(pos: int, board_size: int) -> tuple[int, int]:
    """Convert position to (row, col), 1-based index."""
    pos = abs(pos) - 1
    return divmod(pos, board_size)


def coord_to_pos(row: int, col: int, board_size: int) -> int:
    """Convert (row, col) to position, 1-based index."""
    return row * board_size + col + 1

class ActionSetGeomBoard:

    board_size = 4  # Set this dynamically if needed

    @staticmethod
    def remove(board_state: np.ndarray, object_index: int, direction: str = None) -> np.ndarray:
        board_state[object_index, 1] = -1  # off-board status
        return board_state

    @staticmethod
    def flip(board_state: np.ndarray, object_index: int, direction: str) -> np.ndarray:
        if board_state[object_index, 1] == -1:
            return board_state  # Can't flip if off-board
        current_orientation = board_state[object_index, 2]
        board_state[object_index, 2] = FLIP_TRANSITIONS[current_orientation][direction]
        return board_state

    @staticmethod
    def move(board_state: np.ndarray, object_index: int, direction: str) -> np.ndarray:
        if board_state[object_index, 1] == -1:
            return board_state  # Can't move if off-board

        pos = board_state[object_index, 0]
        row, col = pos_to_coord(pos, ActionSetGeomBoard.board_size)

        if direction == "up":
            row -= 1
        elif direction == "down":
            row += 1
        elif direction == "left":
            col -= 1
        elif direction == "right":
            col += 1

        # Check board bounds
        if not (0 <= row < ActionSetGeomBoard.board_size and 0 <= col < ActionSetGeomBoard.board_size):
            return board_state  # Out of bounds, ignore action

        new_pos = coord_to_pos(row, col, ActionSetGeomBoard.board_size)

        # Set new stack-level based on objects at the new position
        stacks_at_new_pos = board_state[
            (board_state[:, 0] == new_pos) & (board_state[:, 1] >= 0), 1
        ]
        new_stack_level = stacks_at_new_pos.max() + 1 if stacks_at_new_pos.size > 0 else 0

        board_state[object_index, 0] = new_pos
        board_state[object_index, 1] = new_stack_level

        return board_state

    @staticmethod
    def add(board_state: np.ndarray, object_index: int = None, direction: str = None) -> np.ndarray:
        # Add the first available off-board object at a random free position
        off_board_indices = np.where(board_state[:, 1] == -1)[0]
        if off_board_indices.size == 0:
            return board_state  # No objects left off-board to add

        obj_idx = off_board_indices[0] if object_index is None else object_index

        occupied_positions = board_state[board_state[:, 1] >= 0, 0]
        all_positions = set(range(1, ActionSetGeomBoard.board_size ** 2 + 1))
        free_positions = list(all_positions - set(occupied_positions))

        if not free_positions:
            return board_state  # No free positions

        new_pos = np.random.choice(free_positions)
        stacks_at_new_pos = board_state[
            (board_state[:, 0] == new_pos) & (board_state[:, 1] >= 0), 1
        ]
        new_stack_level = stacks_at_new_pos.max() + 1 if stacks_at_new_pos.size > 0 else 0

        board_state[obj_idx, 0] = new_pos
        board_state[obj_idx, 1] = new_stack_level
        return board_state