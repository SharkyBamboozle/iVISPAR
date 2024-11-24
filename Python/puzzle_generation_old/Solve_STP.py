import heapq

def manhattan_distance(pos1, pos2):
    """Calculate the Manhattan distance between two points."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def heuristic(state, goal_states):
    """Calculate the total Manhattan distance of all tiles to their goal positions."""
    total_distance = 0
    for tile, pos in state.items():
        if tile in goal_states:
            total_distance += manhattan_distance(pos, goal_states[tile])
    return total_distance

def get_neighbors(state, n):
    """Generate all valid neighboring states for a given state."""
    neighbors = []
    empty = state[None]  # The empty tile position
    x, y = empty

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < n and 0 <= new_y < n:
            new_state = state.copy()
            for tile, pos in state.items():
                if pos == (new_x, new_y):  # Swap with the empty tile
                    new_state[tile] = empty
            new_state[None] = (new_x, new_y)
            neighbors.append(new_state)
    return neighbors

def a_star(n, initial_tiles, goal_tiles):
    """
    Solve the n x n sliding tile puzzle using A* algorithm.

    :param n: Board size (n x n)
    :param initial_tiles: List of tuples [(tile, (x, y)), ...] representing initial state
    :param goal_tiles: List of tuples [(tile, (x, y)), ...] representing goal state
    :return: List of states from initial to goal, or None if no solution
    """
    initial_state = {tile: pos for tile, pos in initial_tiles}
    goal_states = {tile: pos for tile, pos in goal_tiles}

    # Priority queue for A* search
    open_set = []
    heapq.heappush(open_set, (0, initial_state))
    came_from = {}  # Map to reconstruct the path
    g_score = {tuple(initial_state.items()): 0}
    f_score = {tuple(initial_state.items()): heuristic(initial_state, goal_states)}

    while open_set:
        _, current_state = heapq.heappop(open_set)

        # Check if the current state is the goal state
        if all(current_state[tile] == goal_states[tile] for tile in goal_states):
            path = []
            while current_state in came_from:
                path.append(current_state)
                current_state = came_from[current_state]
            path.append(initial_state)
            return path[::-1]

        # Explore neighbors
        for neighbor in get_neighbors(current_state, n):
            neighbor_key = tuple(neighbor.items())
            tentative_g_score = g_score[tuple(current_state.items())] + 1

            if tentative_g_score < g_score.get(neighbor_key, float('inf')):
                came_from[neighbor_key] = current_state
                g_score[neighbor_key] = tentative_g_score
                f_score[neighbor_key] = tentative_g_score + heuristic(neighbor, goal_states)
                heapq.heappush(open_set, (f_score[neighbor_key], neighbor))

    return None  # No solution found

# Example usage:
n = 5  # Board size
initial_tiles = [
    (1, (0, 0)),
    (2, (0, 1)),
    (3, (0, 2)),
    (4, (1, 0)),
    (5, (1, 1)),
    (None, (1, 2)),  # Empty tile
]
goal_tiles = [
    (1, (0, 0)),
    (2, (0, 1)),
    (3, (0, 2)),
    (4, (1, 0)),
    (5, (1, 1)),
    (None, (1, 2)),  # Empty tile
]

solution = a_star(n, initial_tiles, goal_tiles)
if solution:
    print("Solution found!")
    for step in solution:
        print(step)
else:
    print("No solution exists.")
