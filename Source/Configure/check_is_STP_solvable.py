import numpy as np


def count_inversions(tiles, board_size):
    """Counts the number of inversions in the tile list."""
    flattened = [pos[0] * board_size + pos[1] for pos in tiles]  # Flatten tiles using 1D index
    inversions = 0
    for i in range(len(flattened)):
        for j in range(i + 1, len(flattened)):
            if flattened[i] != 0 and flattened[j] != 0 and flattened[i] > flattened[j]:
                inversions += 1
    return inversions


def get_blank_position(state, board_size):
    """Finds the position of the blank tile and returns its row from the bottom."""
    all_positions = {(row, col) for row in range(board_size) for col in range(board_size)}  # All possible positions
    occupied_positions = {tuple(pos) for pos in state.tolist()}  # Positions that are occupied
    blank_position = list(all_positions - occupied_positions)  # The difference gives the blank tile's position

    if not blank_position:
        raise ValueError("No blank position found in the state.")

    blank_pos = blank_position[0]  # Assume only one blank
    blank_row_from_top = blank_pos[0]  # Row of the blank (0-indexed from the top)
    blank_row_from_bottom = board_size - blank_row_from_top  # Row from bottom
    return blank_row_from_bottom


def is_solvable(state, goal_state=None):
    """
    Check if a sliding tile puzzle is solvable.

    Args:
        state (ndarray): Current state of the sliding tile puzzle as a 2D numpy array of shape (n, 2).

    Returns:
        bool: True if the puzzle is solvable, False otherwise.
    """
    n = state.shape[0]  # Number of tiles
    board_size = int(np.sqrt(n + 1))  # Derive board size (e.g., 3x3 if n=8, 4x4 if n=15)

    # Count inversions in the linearized tile list
    inversions = count_inversions(state, board_size)

    if board_size % 2 == 1:  # Odd-sized board
        return inversions % 2 == 0
    else:  # Even-sized board
        blank_row_from_bottom = get_blank_position(state, board_size)
        return (inversions + blank_row_from_bottom) % 2 == 0


if __name__ == "__main__":
    # Example test cases
    state = np.array([
        [2, 1],
        [2, 2],
        [2, 0],
        [0, 1],
        [1, 2],
        [0, 0],
        [0, 2],
        [1, 0]
    ])

    goal_state = np.array([
        [0, 0],
        [0, 1],
        [0, 2],
        [1, 0],
        [1, 1],
        [1, 2],
        [2, 0],
        [2, 1]
    ])

    result = is_solvable(state, goal_state)
    print(f"Is the state solvable? {'Yes' if result else 'No'}")
