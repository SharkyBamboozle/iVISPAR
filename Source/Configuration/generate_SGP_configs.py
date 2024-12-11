"""Generate Sliding Geom Puzzle (SGP) configuration files"""

# Import statements
import os
import math
import random
import numpy as np
import time
import warnings
from datetime import datetime

from find_shortest_move_sequence import a_star, manhattan_heuristic
from encode_config_to_json import encode_config_to_json
from visualise_configs_statistics import visualise_config_stats


def generate_SGP_configs(board_size, num_geoms_min_max, complexity_min_max, complexity_bin_size, shapes, colors,
                         interval = 60):
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
    config_id = f"SGP_ID_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)
    os.makedirs(config_dir, exist_ok=True)

    # Sampling independently of c2 or c1
    use_c1_c2 = [True, True]
    if not complexity_min_max["c2"]:
        complexity_min_max["c2"]["min"] = 0
        complexity_min_max["c2"]["max"] = 1000
        use_c1_c2[1] = False
        print("Not using c2")
    if not complexity_min_max["c1"]:
        complexity_min_max["c1"]["min"] = 0
        complexity_min_max["c1"]["max"] = 1000
        complexity_min_max["c2"]["min"] = 0
        complexity_min_max["c2"]["max"] = 1000
        use_c1_c2[0] = False
        print("Not using c1 or c2")

    # Initialize nested bins
    complexity_bins = {
        num_geoms: {c1: {
                c2: 0 for c2 in range(complexity_min_max["c2"]["min"], complexity_min_max["c2"]["max"] + 1)}
            for c1 in range(complexity_min_max["c1"]["min"], complexity_min_max["c1"]["max"] + 1)}
        for num_geoms in range(num_geoms_min_max["min"], num_geoms_min_max["max"] + 1)
    }

    # Calculate num of configs
    total_bin_values_checkpoint = 0
    num_configs_current = 0
    num_configs_per_num_geoms = ((complexity_min_max["c1"]["max"] - complexity_min_max["c1"]["min"] +1) *
                                 (complexity_min_max["c2"]["max"] - complexity_min_max["c2"]["min"] +1) *
                                 complexity_bin_size)
    num_configs_total = (num_geoms_min_max['max']-num_geoms_min_max['min']+1) * num_configs_per_num_geoms

    print(f"Generating {config_id}: {num_configs_total} samples of SlidingGeomPuzzle (SGP) configs for "
          f"{board_size}x{board_size} with {num_geoms_min_max['min']}-{num_geoms_min_max['max']} geoms")

    # Sample board states
    sample_board_states = lambda num_geoms: np.stack((
        (idx := np.random.choice(board_size ** 2, num_geoms, replace=False)) // board_size, idx % board_size), axis=1)

    # Sample initial and goal states until complexity bins are filled with bin size amount of samples
    for i, num_geoms in enumerate(range(num_geoms_min_max['min'], num_geoms_min_max['max']+1)):
        print(f"Start sampling SlidingGeomPuzzle configs for {num_geoms} geoms.")

        # Timer settings
        last_checked_time = time.time()  # Initialize the last checked time

        # Track used combinations
        complexity_bins = np.zeros((complexity_min_max["c1"]["max"] - complexity_min_max["c1"]["min"] +1,
                                    complexity_min_max["c2"]["max"] - complexity_min_max["c2"]["min"] +1), dtype=int)
        seen_state_combinations = set()

        def has_unfilled_c1_bins_np(complexity_bins, found_complexity, complexity_bin_size, c1_range):
            c1_indices = [i for i, c1 in enumerate(c1_range) if c1 <= found_complexity]
            c1_sums = complexity_bins[:, c1_indices, :].sum(axis=2)  # Sum over c2 bins
            return np.any(c1_sums < complexity_bin_size)

        while True:
            # Check progress every 'interval' seconds
            if time.time() - last_checked_time >= interval:
                # Evaluate condition for breaking the loop
                if total_bin_values_checkpoint == num_configs_current:
                    warnings.warn(f"Abort generating further SGP configs, no configs found for {interval} seconds")
                    #break # Break in case you want simulation to stop after a time interval

                print(f"Checking at {datetime.now().strftime('%H:%M')}: {num_configs_current}/{num_configs_total} "
                      f"new configs, checked {len(seen_state_combinations)} total configs")
                total_bin_values_checkpoint = num_configs_current
                last_checked_time = time.time()

            # Sample initial and goal states
            init_state = sample_board_states(num_geoms)
            goal_state = sample_board_states(num_geoms)

            # Create a hashable unique combination of init and goal state
            state_combination = (tuple(map(tuple, init_state)), tuple(map(tuple, goal_state)))

            # Check if the combination is already seen
            if state_combination in seen_state_combinations:
                continue  # Skip this iteration if already sampled
            #elif manhattan_heuristic(init_state, goal_state) add some check here
            else: # Add the combination to the seen set
                seen_state_combinations.add(state_combination)

            # Sample geoms without replacement
            geoms_sample = random.sample(geoms, num_geoms)

            # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
            shortest_move_sequence = a_star(board_size, init_state, goal_state)
            complexity =  {
                "c1": len(shortest_move_sequence)-1,
                "c2": (len(shortest_move_sequence)-1 - manhattan_heuristic(init_state, goal_state))//2
            }

            # Check if the complexity bin is valid
            if (num_geoms not in complexity_bins or  # Check if num_geoms exists in the top-most dictionary
                    complexity['c1'] not in complexity_bins[num_geoms] or  # Check if c1 exists in the next level
                    complexity['c2'] not in complexity_bins[num_geoms][complexity['c1']] or  # Check if c2 exists in the inner dictionary
                    complexity_bins[num_geoms][complexity['c1']][complexity['c2']] >= complexity_bin_size):  # Check if the bin size is exceeded
                continue

            # Increment the corresponding bin
            if use_c1_c2[0] and use_c1_c2[1]:  # Both c1 and c2 are used
                complexity_bins[num_geoms][complexity['c1']][complexity['c2']] += 1
            elif not use_c1_c2[1]:  # Only c1 is used, increment all c2 bins
                for c2 in complexity_bins[num_geoms][complexity['c1']]:
                    complexity_bins[num_geoms][complexity['c1']][c2] += 1
            elif not use_c1_c2[0]:  # Only c2 is used, increment all c1 bins and their respective c2 bins
                for c1 in complexity_bins[num_geoms]:
                    for c2 in complexity_bins[num_geoms][c1]:
                        complexity_bins[num_geoms][c1][c2] += 1

            # Serialize SGP configuration to JSON file
            encode_config_to_json(board_size, state_combination, geoms_sample,
                                  complexity, complexity_bins, shortest_move_sequence,
                                  config_id, config_dir)

            # Check if all bins are full
            num_configs_current = sum(sum(sum(sub_bin.values())
                for sub_bin in c1_bins.values())
                for c1_bins in complexity_bins.values()
            )
            if num_configs_current == num_configs_per_num_geoms *(i+1):
                print(f"Successfully finished building all configurations for {num_geoms} geoms")
                break

    return config_id


if __name__ == "__main__":
    # Parameters
    board_size = 4
    num_geoms_min_max = {"min": 4, "max": 7}
    complexity_min_max = {"c1": {"min": 8, "max": 14},  # smallest and highest c1 complexity to be considered
                          "c2": {"min": 0, "max": 2}}  # smallest and highest c2 complexity to be considered
    complexity_bin_size = 1  # amount of puzzle configs per complexity bin
    shapes = ['cube', 'sphere', 'pyramid']#, 'cylinder', 'cone', 'prism']
    colors = ['red', 'green', 'blue']#, 'yellow', 'purple', 'orange']

    # Generate Sliding Geom Puzzle (SGP) configuration files
    config_id = generate_SGP_configs(board_size, num_geoms_min_max, complexity_min_max, complexity_bin_size, shapes, colors)
    print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

    # Visualise config stats
    visualise_config_stats(config_id)