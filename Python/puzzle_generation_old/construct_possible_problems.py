import itertools
import numpy as np
from collections import defaultdict


def generate_symmetry_operations(size):
    """Generate all symmetry operations for an x by x grid."""

    def rotate(grid):
        return np.rot90(grid)

    def reflect_h(grid):
        return np.flipud(grid)

    def reflect_v(grid):
        return np.fliplr(grid)

    def reflect_d1(grid):
        return np.transpose(grid)

    def reflect_d2(grid):
        return np.flipud(np.transpose(grid))

    operations = []
    grid = np.arange(size * size).reshape((size, size))
    grids = []

    # Generate all 8 symmetry operations
    for k in range(4):
        rot_grid = np.rot90(grid, k)
        grids.append(rot_grid)
        grids.append(np.fliplr(rot_grid))

    # Convert grids to flat tuple representations for hashing
    operations = [tuple(g.flatten()) for g in grids]
    unique_operations = list(set(operations))
    return unique_operations


def canonical_form(configuration, symmetry_operations):
    """Compute the canonical form of a configuration under symmetry operations."""
    configs = []
    for op in symmetry_operations:
        transformed = [configuration[i] for i in op]
        configs.append(tuple(transformed))
    return min(configs)


def generate_initial_configurations(size, num_tiles):
    """Generate all unique initial configurations."""
    n = size * size
    positions = list(range(n))

    # Generate all combinations of positions to place tiles
    tile_positions = list(itertools.combinations(positions, num_tiles))

    # Prepare symmetry operations
    symmetry_ops = generate_symmetry_operations(size)

    # Use a set to store unique canonical forms
    unique_configs = set()

    for pos in tile_positions:
        # Create configuration: 1 for tile, 0 for empty
        config = [0] * n
        for p in pos:
            config[p] = 1
        # Compute canonical form
        canonical = canonical_form(config, symmetry_ops)
        unique_configs.add(canonical)

    return list(unique_configs)


def generate_goal_configurations(size, num_tiles):
    """Generate all goal configurations with numbered tiles."""
    n = size * size
    positions = list(range(n))
    # Generate all permutations of positions to place the tiles
    tile_positions = list(itertools.permutations(positions, num_tiles))
    # Generate all permutations of tile numbers
    tile_numbers = list(itertools.permutations(range(1, num_tiles + 1)))

    goal_configs = []
    for pos in tile_positions:
        for nums in tile_numbers:
            # Create configuration: 0 for empty, tile number for tile
            config = [0] * n
            for p, num in zip(pos, nums):
                config[p] = num
            goal_configs.append(tuple(config))
    return goal_configs


def generate_problems(size, num_tiles):
    """Generate all possible problems under the specified constraints."""
    initial_configs = generate_initial_configurations(size, num_tiles)
    goal_configs = generate_goal_configurations(size, num_tiles)

    problems = []
    for init_config in initial_configs:
        for goal_config in goal_configs:
            problems.append((init_config, goal_config))
    return problems


def print_configuration(config, size):
    """Helper function to print the grid configuration."""
    grid = np.array(config).reshape((size, size))
    print(grid)


# Example usage for small size and number of tiles
size = 2
num_tiles = 2

problems = generate_problems(size, num_tiles)
print(f"Total number of problems: {len(problems)}")

# Print some example problems
for idx, (init, goal) in enumerate(problems[:5]):
    print(f"\nProblem {idx + 1}:")
    print("Initial Configuration:")
    print_configuration(init, size)
    print("Goal Configuration:")
    print_configuration(goal, size)
