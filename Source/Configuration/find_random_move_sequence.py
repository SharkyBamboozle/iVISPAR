import numpy as np
import random


def get_neighbors(state, n):
    """
    Generate all valid neighboring states for a given state.
    A neighbor is obtained by sliding a tile into an adjacent empty position.
    """
    neighbors = []
    tiles_set = set(map(tuple, state))  # Convert tiles' coordinates to a set for fast lookup
    for i, (x, y) in enumerate(state):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Possible moves: up, down, left, right
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < n and 0 <= new_y < n and (new_x, new_y) not in tiles_set:
                new_state = state.copy()
                new_state[i] = [new_x, new_y]
                neighbors.append(new_state)
    return neighbors


def generate_random_valid_path(n, initial_state, max_steps=100):
    """
    Generate a path of n valid moves for a sliding tile puzzle, starting from initial_state.

    Args:
        n (int): Board size (n x n grid).
        initial_state (list): List of starting tile positions (list of [x, y] pairs).
        max_steps (int): Number of random valid moves to generate.

    Returns:
        list: List of states from initial to final, representing the moves taken.
    """
    initial_state = np.array(initial_state)
    path = [initial_state.tolist()]  # Initial state is the first state in the path
    current_state = initial_state.copy()

    for step in range(max_steps):
        neighbors = get_neighbors(current_state, n)

        if not neighbors:
            print(f"No more neighbors to explore at step {step}. Ending early.")
            break

        # Randomly pick one of the valid neighboring states
        current_state = random.choice(neighbors)
        path.append(current_state.tolist())

    return path


def generate_random_invalid_path(n, initial_state, max_steps=100):
    """
    Generate a path of n moves for a sliding tile puzzle, starting from initial_state.
    This version does not filter out invalid moves. Instead, if an invalid move is selected,
    the current state is repeated for the next step, but the invalid move is still recorded.

    Args:
        n (int): Board size (n x n grid).
        initial_state (list): List of starting tile positions (list of [x, y] pairs).
        max_steps (int): Number of random moves to generate.

    Returns:
        list: List of states from initial to final, representing the moves taken.
    """
    initial_state = np.array(initial_state)
    path = [initial_state.tolist()]  # Initial state is the first state in the path
    valid_state = initial_state.copy()  # The state that we revert to if the move is invalid

    for step in range(max_steps):
        # Randomly pick a tile to move
        random_tile_idx = random.randint(0, len(valid_state) - 1)
        x, y = valid_state[random_tile_idx]

        # Randomly pick a move direction (up, down, left, right)
        dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        new_x, new_y = x + dx, y + dy

        # Create the new potential state
        new_state = valid_state.copy()
        new_state[random_tile_idx] = [new_x, new_y]

        # Check if the new position is valid
        if 0 <= new_x < n and 0 <= new_y < n and (new_x, new_y) not in map(tuple, valid_state):
            valid_state = new_state.copy()  # Accept the move and update the valid state

        # Record the new state, even if it's invalid
        path.append(new_state.tolist())  # Always add the new state, even if invalid

    return path


if __name__ == "__main__":
    board_size = 5  # 5x5 grid
    initial_state = np.array([
        [1, 0],
        [4, 1],
        [3, 0],
        [0, 3],
        [1, 4],
    ])
    max_steps = 100  # Number of random valid moves

    print("\n--- Random Valid Path ---")
    path_valid = generate_random_valid_path(board_size, initial_state, max_steps)
    for i, state in enumerate(path_valid):
        print(f"Step {i}: {state}")

    print("\n--- Random Path With Repeats ---")
    path_with_repeats = generate_random_invalid_path(board_size, initial_state, max_steps)
    for i, state in enumerate(path_with_repeats):
        print(f"Step {i}: {state}")
