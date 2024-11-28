import heapq
import numpy as np
import time


def manhattan_heuristic(initial_states, goal_states):
    """Calculate the cumulative Manhattan distance of all geoms from their initial to their goal positions."""

    # Ensure the arrays have the same shape
    assert initial_states.shape == goal_states.shape, "Initial and goal states must have the same shape."

    # Calculate Manhattan distances
    distances = np.abs(initial_states - goal_states).sum(axis=1)  # Sum differences along coordinates for each object

    # Return cumulative Manhattan distance
    return int(distances.sum())

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
                # Generate a new state by moving the current tile
                new_state = state.copy()
                new_state[i] = [new_x, new_y]
                neighbors.append(new_state)
    return neighbors

def a_star_2(n, initial_state, goal_state):
    """
    Solve the n x n sliding tile puzzle using A* algorithm.

    :param n: Board size (n x n)
    :param initial_state: np.array of shape (5, 2) for the starting tile positions
    :param goal_state: np.array of shape (5, 2) for the goal tile positions
    :return: List of states from initial to goal, or None if no solution
    """
    initial_state = np.array(initial_state)
    goal_state = np.array(goal_state)

    # Priority queue for A* search
    open_set = []
    heapq.heappush(open_set, (0, tuple(map(tuple, initial_state))))
    came_from = {}  # Map to reconstruct the path
    g_score = {tuple(map(tuple, initial_state)): 0}
    f_score = {tuple(map(tuple, initial_state)): manhattan_heuristic(initial_state, goal_state)}

    while open_set:
        _, current_tuple = heapq.heappop(open_set)
        current_state = np.array(current_tuple)

        # Check if the current state is the goal state
        if np.array_equal(current_state, goal_state):
            path = []
            while current_tuple in came_from:
                path.append(current_state.tolist())
                current_tuple = came_from[current_tuple]
                current_state = np.array(current_tuple)
            path.append(initial_state.tolist())
            return path[::-1]

        # Explore neighbors
        for neighbor in get_neighbors(current_state, n):
            neighbor_tuple = tuple(map(tuple, neighbor))
            tentative_g_score = g_score[current_tuple] + 1

            if tentative_g_score < g_score.get(neighbor_tuple, float('inf')):
                came_from[neighbor_tuple] = current_tuple
                g_score[neighbor_tuple] = tentative_g_score
                f_score[neighbor_tuple] = tentative_g_score + manhattan_heuristic(neighbor, goal_state)
                heapq.heappush(open_set, (f_score[neighbor_tuple], neighbor_tuple))

    return None  # No solution found


def a_star(n, initial_state, goal_state):
    """
    Solve the n x n sliding tile puzzle using A* algorithm and return a JSON-compatible path.

    :param n: Board size (n x n)
    :param initial_state: List of starting tile positions (list of [x, y] pairs)
    :param goal_state: List of goal tile positions (list of [x, y] pairs)
    :return: List of states from initial to goal in JSON-compatible format, or None if no solution
    """
    initial_state = np.array(initial_state)
    goal_state = np.array(goal_state)

    # Priority queue for A* search
    open_set = []
    heapq.heappush(open_set, (0, tuple(map(tuple, initial_state))))
    came_from = {}  # Map to reconstruct the path
    g_score = {tuple(map(tuple, initial_state)): 0}
    f_score = {tuple(map(tuple, initial_state)): manhattan_heuristic(initial_state, goal_state)}

    while open_set:
        _, current_tuple = heapq.heappop(open_set)
        current_state = np.array(current_tuple)

        # Check if the current state is the goal state
        if np.array_equal(current_state, goal_state):
            path = []
            while current_tuple in came_from:
                path.append([[int(coord) for coord in pair] for pair in current_tuple])  # Ensure JSON-compatible
                current_tuple = came_from[current_tuple]
            path.append([[int(coord) for coord in pair] for pair in tuple(map(tuple, initial_state))])  # Add initial state
            return path[::-1]

        # Explore neighbors
        for neighbor in get_neighbors(current_state, n):
            neighbor_tuple = tuple(map(tuple, neighbor))
            tentative_g_score = g_score[current_tuple] + 1

            if tentative_g_score < g_score.get(neighbor_tuple, float('inf')):
                came_from[neighbor_tuple] = current_tuple
                g_score[neighbor_tuple] = tentative_g_score
                f_score[neighbor_tuple] = tentative_g_score + manhattan_heuristic(neighbor, goal_state)
                heapq.heappush(open_set, (f_score[neighbor_tuple], neighbor_tuple))

    return None  # No solution found


def solve_with_timing(n, initial_state, goal_state):
    """
    Solve the sliding tile puzzle and measure the time taken.
    """
    start_time = time.time()  # Start the timer
    solution = a_star(n, initial_state, goal_state)
    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time
    return solution, elapsed_time

if __name__ == "__main__":
    n = 5  # Board size
    initial_state = np.array([
        [1, 0],
        [4, 1],
        [3, 0],
        [0, 3],
        [1, 4],
    ])
    goal_state = np.array([
        [0, 2],
        [1, 1],
        [4, 0],
        [3, 3],
        [1, 0],
    ])

    solution, elapsed_time = solve_with_timing(n, initial_state, goal_state)

    if solution:
        print("Solution found!")
        print(f"Time taken: {elapsed_time:.4f} seconds")
        for step in solution:
            print(step)
    else:
        print("No solution exists.")
        print(f"Time taken: {elapsed_time:.4f} seconds")
