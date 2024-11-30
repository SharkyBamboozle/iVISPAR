"""Generate Scene Understanding Task (SUT) configuration files"""

# Import statements
import os
import random
import numpy as np
import time
import warnings
import math
from datetime import datetime

from find_shortest_move_sequence import a_star, manhattan_heuristic
from encode_config_to_json import encode_config_to_json
from visualise_configs_statistics import visualise_config_stats


def generate_sut_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors):
    """

    Args:
        board_size:
        num_geoms_min_max:
        complexity_bin_size:
        shapes:
        colors:

    Returns:

    """

    # Validate parameters
    if num_geoms_min_max['max'] > board_size ** 2:
        raise ValueError("Number of geoms exceeds the total cells on the board.")
    geoms = [(shape, color) for shape in shapes for color in colors]
    if num_geoms_min_max['max'] > len(geoms):
        raise ValueError("Number of geoms exceeds the total number of geoms available.")
    total_combinations = math.comb(num_geoms_min_max['min'] + board_size**2 - 1, num_geoms_min_max['min'])
    if total_combinations < complexity_bin_size:
        raise ValueError(f"Bin size ({complexity_bin_size}) exceeds the total number of board state combinations "
                         f"({total_combinations}) available.")

    # Set up directories
    config_id = f"SUT_ID_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)
    os.makedirs(config_dir, exist_ok=True)

    # Initialize nested bins
    complexity_bins = {
        c1: {c2: 0 for c2 in range(0, 1000 + 1)}
        for c1 in range(0, 1000 + 1)
    }
    total_bin_values_checkpoint = 0
    total_bin_values = 0
    total_bin_size = complexity_bin_size *  sum(len(c2_bins) for c2_bins in complexity_bins.values())
    total_config_num = (num_geoms_min_max['max']-num_geoms_min_max['min']) * complexity_bin_size
    print(f"Generating {config_id}: {total_config_num} samples of SUT configs for {board_size}x{board_size} with "
          f"{num_geoms_min_max['min']}-{num_geoms_min_max['max']} geoms")

    # Track used combinations
    seen_state_combinations = set()

    # Sample board states
    sample_board_states = lambda num_geoms: np.stack((
        (idx := np.random.choice(board_size ** 2, num_geoms, replace=False)) // board_size,
        idx % board_size), axis=1)

    # Timer settings
    interval = 600
    last_checked_time = time.time()  # Initialize the last checked time

    # Sample initial and goal states until complexity bins are filled with bin size amount of samples
    for num_geoms in range(num_geoms_min_max['min'], num_geoms_min_max['max']):
        num_found = 0  # Track the number of unique states found for this num_geoms
        while num_found < complexity_bin_size:
            # Check progress every 'interval' seconds
            if time.time() - last_checked_time >= interval:
                # Evaluate condition for breaking the loop
                if total_bin_values_checkpoint == total_bin_values:
                    warnings.warn(f"Abort generating further SUT configs, no configs found for {interval} seconds")
                    #break

                print(f"Checking at {datetime.now().strftime('%H:%M')}: {total_bin_values}/{total_bin_size} new configs")
                total_bin_values_checkpoint = total_bin_values
                last_checked_time = time.time()

            # Sample goal states (initial states are not used in SUT)
            goal_state = sample_board_states(num_geoms)
            init_state = np.zeros_like(goal_state, dtype=int)


            # Create a hashable unique combination of init and goal state
            state_combination = (tuple(map(tuple, init_state)), tuple(map(tuple, goal_state)))

            # Check if the combination is already seen
            if state_combination in seen_state_combinations:
                continue  # Skip this iteration if already sampled
            else: # Add the combination to the seen set
                seen_state_combinations.add(state_combination)
                num_found += 1  # Increment only when a new unique combination is added

            # Sample geoms without replacement
            geoms_sample = random.sample(geoms, num_geoms)

            # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
            shortest_move_sequence = a_star(board_size, init_state, goal_state)
            complexity =  {
                "c1": num_geoms,
                "c2": 0
            }

            # Increment the corresponding bin
            complexity_bins[complexity['c1']][complexity['c2']] += 1

            # Serialize SUT configuration to JSON file
            encode_config_to_json(board_size, state_combination, geoms_sample,
                                  complexity, complexity_bins, shortest_move_sequence,
                                  config_id, config_dir)

            # Check if all bins are full
            total_bin_values = sum(sum(sub_bin.values()) for sub_bin in complexity_bins.values())
            if total_bin_values == total_bin_size:
                print("Successfully finished building all configurations")
                break

    return config_id


if __name__ == "__main__":
    # Parameters
    board_size = 4
    num_geoms_min_max = {"min": 1, "max": 9}
    complexity_bin_size = 10 # amount of puzzle configs per complexity bin
    shapes = ['cube', 'sphere', 'pyramid']#, 'cylinder', 'cone', 'prism']
    colors = ['red', 'green', 'blue']#, 'yellow', 'purple', 'orange']

    # Generate Scene Understanding Task (SUT) configuration files
    config_id = generate_sut_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors)
    print(f"Finished Generate Scene Understanding Task (SUT) configuration files with ID: {config_id}")

    # Visualize statistics of the generated config files
    visualise_config_stats(config_id)