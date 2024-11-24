import math

def calculate_total_configurations(n, m, numbered= True):
    """
    Calculate the total number of initial-to-goal configurations
    for a sliding tile puzzle.

    Args:
        n (int): Size of the board (n x n).
        m (int): Number of numbered tiles on the board.

    Returns:
        int: Total number of initial-to-goal configurations.
    """
    # Total number of positions on the board
    total_positions = n * n

    # Validate input
    if m > total_positions or m < 0:
        return 0

    # Calculate configurations for a single board
    position_combinations = math.comb(total_positions, m)  # Choose positions for m tiles
    #print(position_combinations)
    if numbered:
        tile_permutations = math.factorial(m)                 # Permute the m tiles
    else:
        tile_permutations = 1
    #print(tile_permutations)
    configurations_per_board = position_combinations * tile_permutations
    #print(configurations_per_board)

    # Total initial-to-goal configurations
    total_configurations = configurations_per_board ** 2
    #print(configurations_per_board*configurations_per_board)

    return total_configurations

# Example usage
n = 5  # 2x2 board
m = 5  # 1 numbered tile

for i in range(1,6):
    for j in range(1,6):
        print(f"{i} by {i} with {j} geoms")
        print(f"Total configurations: {calculate_total_configurations(i, j)}")
        print()


print("_______________")
for i in range(1,6):
    for j in range(1,6):
        total_positions = i * i
        position_combinations = math.comb(total_positions, j)  # Choose positions for m tiles
        print(f"{i} by {i} with {j} geoms")
        print(f"Total configurations: {position_combinations}")
        print()
