"""Generate Sliding Geom Puzzle (SGP) configuration files"""

# Import statements
import os
import numpy as np
import pandas as pd
import time
import warnings
from datetime import datetime
import hashlib
import zlib
import pickle

import configuration_utilities as util
from find_shortest_move_sequence import a_star, find_config_by_random_expand
from check_is_STP_solvable import is_solvable
from encode_config_to_json import encode_STP_config_to_json
from Source.Plot.visualise_configs_statistics import visualise_config_stats
from find_random_move_sequence import generate_random_valid_path, generate_random_invalid_path


def validate_parameters(complexity_min_max, board_size, complexity_bin_size):
    # Validate complexity ranges
    for key, value in complexity_min_max.items():
        if value["min"] > value["max"]:
            raise ValueError(f"Invalid {key} range: {value}")

def sample_board_states(num_geoms, board_size):
    idx = np.random.choice(board_size ** 2, num_geoms, replace=False)
    return np.stack(((idx // board_size), (idx % board_size)), axis=1)


def has_unfilled_c1_bins_np(complexity_bins, found_complexity, complexity_bin_size, c1_range):
    c1_indices = [i for i, c1 in enumerate(c1_range) if c1 <= found_complexity]
    c1_sums = complexity_bins[:, c1_indices, :].sum(axis=2)  # Sum over c2 bins
    return np.any(c1_sums < complexity_bin_size)


def generate_goal_state(num_elements, board_size):
    """
    Generate the goal state for a sliding tile puzzle, starting from the top-left corner
    and filling downwards in each column, but starting from the bottom row first.

    Args:
        num_elements (int): The number of tiles to be placed in the goal state.
        board_size (int): The size of the board (n x n).

    Returns:
        np.ndarray: An array where each row represents the (x, y) coordinate of a tile.
    """
    # Generate a grid of coordinates (row, col) but with columns as the major index and rows reversed
    coordinates = [(row, col) for col in reversed(range(board_size)) for row in range(board_size)]

    # Select only as many coordinates as needed for the number of elements
    goal_state = coordinates[:num_elements]

    # Convert to a NumPy array for consistency
    goal_state_array = np.array(goal_state, dtype=int)

    return goal_state_array

# Compress the state with zlib
def compress_state(init_state, goal_state):
    state_data = pickle.dumps((init_state, goal_state))
    compressed_state = zlib.compress(state_data)
    return compressed_state

def get_md5_hash(state_str):
    """Convert the state string to an MD5 hash."""
    return hashlib.md5(state_str.encode()).hexdigest()

def compress_with_zlib(state_combination):
    """Compress the state combination using zlib."""
    state_str = str(state_combination)  # Convert the state tuple to a string
    return zlib.compress(state_str.encode())  # Compress the encoded string and return bytes


def generate_STP_configs(board_size, complexity_min_max, complexity_bin_size, interval = 20):
    """

    Args:
        board_size:
        num_geoms:
        complexity_min_max:
        complexity_bin_size:
        shapes:
        colors:

    Returns:

    """

    validate_parameters(complexity_min_max, board_size, complexity_bin_size)

    # Set up directories
    config_id = f"STP_ID_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)
    os.makedirs(config_dir, exist_ok=True)

    # Sampling independently of c2 or c1
    use_c1 = True
    if not complexity_min_max["c1"]:
        complexity_min_max["c1"]["min"] = 0
        complexity_min_max["c1"]["max"] = 1000
        complexity_min_max["c2"]["min"] = 0
        complexity_min_max["c2"]["max"] = 1000
        use_c1 = False
        print("Not using c1")

    # Initialize nested bins
    complexity_range = {"c1": range(complexity_min_max["c1"]["min"], complexity_min_max["c1"]["max"] + 1)}

    # Calculate num of configs
    num_configs_total = ((complexity_min_max["c1"]["max"] - complexity_min_max["c1"]["min"] +1) *
                                 complexity_bin_size)

    print(f"Generating {config_id}: {num_configs_total} samples of SlidingTilePuzzle (STP) configs for "
          f"{board_size}x{board_size}")

    # Sample initial and goal states until complexity bins are filled with bin size amount of samples
    # Track used combinations
    complexity_bins = pd.Series(0, index=complexity_range["c1"])
    seen_state_combinations = set()
    total_bin_values_checkpoint = 0
    last_checked_time = time.time()  # Initialize the last checked time
    num_geoms = board_size**2-1
    goal_state = generate_goal_state(num_geoms, board_size)
    #pbar = tqdm(total=100, desc="Manual Progress")

    for path_length in range(complexity_min_max['c1']['min'], complexity_min_max['c1']['max']+1):
        while True:
            # Check progress every 'interval' seconds
            if time.time() - last_checked_time >= interval:
                num_configs_current = complexity_bins.sum().sum()
                # Evaluate condition for breaking the loop
                if total_bin_values_checkpoint == num_configs_current:
                    warnings.warn(f"Abort generating further SGP configs, no configs found for {interval} seconds")
                    #break # Break in case you want simulation to stop after a time interval

                print(f"Checking at {datetime.now().strftime('%H:%M')}: {num_configs_current}/{num_configs_total} "
                      f"new configs, checked {len(seen_state_combinations):,} total configs")
                #how_many_solutions = len(seen_state_combinations)/1000000
                #pbar.update(how_many_solutions)  # Manually update the progress by 10 units
                total_bin_values_checkpoint = num_configs_current
                last_checked_time = time.time()

            # Sample initial and goal states
            init_state = find_config_by_random_expand(board_size, goal_state, path_length, max_steps=1000)

            # Create a hashable unique combination of init and goal state
            state_combination = (tuple(map(tuple, init_state)), tuple(map(tuple, goal_state)))

            # Compress and check if the state exists
            compressed_state = compress_state(init_state, goal_state)
            if compressed_state in seen_state_combinations:
                continue  # Skip this iteration if already sampled
                print("seen")
            else:
                seen_state_combinations.add(compressed_state)

            if not is_solvable(init_state):
                print("Unsolvable")
                continue

            # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
            shortest_move_sequence = a_star(board_size, init_state, goal_state, max_depth=complexity_min_max["c1"]["max"]+10)
            if shortest_move_sequence==None:
                #print("A* None")
                continue
            random_valid_move_sequence = generate_random_valid_path(board_size, init_state)
            random_invalid_move_sequence = generate_random_invalid_path(board_size, init_state)


            complexity =  {
                "c1": len(shortest_move_sequence)-1,
            }

            # Check if the complexity bin is valid
            if complexity['c1'] not in complexity_bins.index:
                print("Invalid c1")
                continue

            # Increment bins based on the flags
            if use_c1:  # Both c1 and c2 are used
                complexity_bins.loc[complexity["c1"]] += 1

            bin_fill = complexity_bins.loc[complexity["c1"]]

            # Serialize SGP configuration to JSON file
            encode_STP_config_to_json(board_size, state_combination,
                                  complexity, bin_fill, shortest_move_sequence,
                                  random_valid_move_sequence, random_invalid_move_sequence,
                                  config_id, config_dir)

            # Check if all bins are full
            if (complexity_bins >= complexity_bin_size).all().all():
                print(f"Successfully finished building all configurations for {num_geoms} geoms")
                break

    #pbar.close()  # Close the progress bar
    return config_id


if __name__ == "__main__":
    # Load parameters from the JSON file
    params = util.load_params_from_json('111params_STP_config_example.json')

    # Generate Sliding Tile Puzzle (STP) configuration files
    config_id = generate_STP_configs(board_size=params.get('board_size', 5),
                                     complexity_min_max=params.get('complexity_min_max', {"c1": {"min": 16, "max": 16}}),
                                     complexity_bin_size=params.get('complexity_bin_size', 10))
    print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

    # Visualise config stats
    visualise_config_stats(config_id)