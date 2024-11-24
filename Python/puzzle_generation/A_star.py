import heapq
import numpy as np
import time

def manhattan_distance(pos1, pos2):
    """Calculate the Manhattan distance between two points."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def heuristic(state, goal_state):
    """Calculate the total Manhattan distance of all tiles to their goal positions."""
    return sum(manhattan_distance(state[i], goal_state[i]) for i in range(len(state)))

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

def a_star(n, initial_state, goal_state):
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
    f_score = {tuple(map(tuple, initial_state)): heuristic(initial_state, goal_state)}

    while open_set:
        _, current_tuple = heapq.heappop(open_set)
        current_state = np.array(current_tuple)

        # Check if the current state is the goal state
        if np.array_equal(current_state, goal_state):
            path = []
            while current_tuple in came_from:
                path.append(current_state)
                current_tuple = came_from[current_tuple]
                current_state = np.array(current_tuple)
            path.append(initial_state)
            return path[::-1]

        # Explore neighbors
        for neighbor in get_neighbors(current_state, n):
            neighbor_tuple = tuple(map(tuple, neighbor))
            tentative_g_score = g_score[current_tuple] + 1

            if tentative_g_score < g_score.get(neighbor_tuple, float('inf')):
                came_from[neighbor_tuple] = current_tuple
                g_score[neighbor_tuple] = tentative_g_score
                f_score[neighbor_tuple] = tentative_g_score + heuristic(neighbor, goal_state)
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
