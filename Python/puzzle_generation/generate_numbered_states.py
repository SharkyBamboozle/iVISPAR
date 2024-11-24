import numpy as np
from itertools import permutations

def generate_tile_coordinates_np(grid_size, num_tiles):
    if num_tiles > grid_size ** 2:
        raise ValueError("Number of tiles exceeds the total cells in the grid.")

    # Generate all grid coordinates as a numpy array
    grid_coords = np.array([(row, col) for row in range(grid_size) for col in range(grid_size)])

    # Generate all possible solutions using permutations
    solutions = np.array([np.array(selected_coords) for selected_coords in permutations(grid_coords, num_tiles)])

    # Shuffle the solutions using np.random.permutation
    initial_states = solutions[np.random.permutation(len(solutions))]
    goal_states =  solutions[np.random.permutation(len(solutions))]

    return initial_states, goal_states


if __name__ == "__main__":
    # Example usage
    x = 5  # Grid size (3x3)
    n = 5  # Number of tiles

    solutions = generate_tile_coordinates_np(x, n)

    print(f"Total solutions: {len(solutions)}")
    print("First 5 solutions (as numpy arrays):")
    for i, solution in enumerate(solutions[:5], start=1):  # Show first 5 solutions
        print(f"Solution {i}:\n{solution}")
