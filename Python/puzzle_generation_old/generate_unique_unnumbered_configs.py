from itertools import permutations
import numpy as np


def is_symmetric(grid, solutions):
    """Check if a grid configuration or its symmetry exists in solutions."""
    rotations = [np.rot90(grid, k=i) for i in range(4)]
    reflections = [np.flip(grid, axis=0), np.flip(grid, axis=1)]
    symmetries = rotations + reflections

    for sym in symmetries:
        if any(np.array_equal(sym, sol) for sol in solutions):
            return True
    return False


def generate_coordinates(x, n):
    """Generate unique tile configurations in an x by x grid."""
    # Generate all possible positions for n tiles in the grid
    positions = [(i, j) for i in range(x) for j in range(x)]
    solutions = []

    for combo in permutations(positions, n):
        grid = np.zeros((x, x), dtype=int)
        for (i, j) in combo:
            grid[i, j] = 1  # Mark tile position

        if not is_symmetric(grid, solutions):
            solutions.append(grid)

    return solutions


def display_solutions(solutions):
    """Display all unique solutions."""
    for i, sol in enumerate(solutions):
        print(f"Solution {i + 1}:")
        print(sol)
        print()


# Example Usage 
x = 4  # Grid size
n = 1  # Number of tiles
unique_solutions = generate_coordinates(x, n)
display_solutions(unique_solutions)

print(f"Total unique solutions: {len(unique_solutions)}")