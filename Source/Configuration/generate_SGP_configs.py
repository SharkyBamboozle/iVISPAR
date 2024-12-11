"""Generate Sliding Geom Puzzle (SGP) configuration files"""

# Import statements
import os
import math
import random
import numpy as np
import pandas as pd
import time
import warnings
from datetime import datetime

from find_shortest_move_sequence import a_star, calculate_manhattan_heuristic
from encode_config_to_json import encode_SGP_config_to_json
from visualise_configs_statistics import visualise_config_stats
from find_random_move_sequence import generate_random_valid_path, generate_random_invalid_path


def validate_parameters(complexity_min_max, num_geoms_min_max, board_size, num_geoms, complexity_bin_size):
    # Validate complexity ranges
    for key, value in complexity_min_max.items():
        if value["min"] > value["max"]:
            raise ValueError(f"Invalid {key} range: {value}")

    # Validate the number of geoms
    if num_geoms_min_max['max'] > board_size ** 2:
        raise ValueError("Number of geoms exceeds the total cells on the board.")

    if num_geoms_min_max['max'] > num_geoms:
        raise ValueError("Number of geoms exceeds the total number of geoms available.")

    # Validate complexity bin size
    total_combinations = math.comb(num_geoms_min_max['min'] + board_size ** 2 - 1, num_geoms_min_max['min'])
    if total_combinations < complexity_bin_size:
        raise ValueError(f"Bin size ({complexity_bin_size}) exceeds the total number of board state combinations "
            f"({total_combinations}) available.")


def sample_board_states(num_geoms, board_size):
    idx = np.random.choice(board_size ** 2, num_geoms, replace=False)
    return np.stack(((idx // board_size), (idx % board_size)), axis=1)


def has_unfilled_c1_bins_np(complexity_bins, found_complexity, complexity_bin_size, c1_range):
    c1_indices = [i for i, c1 in enumerate(c1_range) if c1 <= found_complexity]
    c1_sums = complexity_bins[:, c1_indices, :].sum(axis=2)  # Sum over c2 bins
    return np.any(c1_sums < complexity_bin_size)


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

    geoms = [(shape, color) for shape in shapes for color in colors]
    validate_parameters(complexity_min_max, num_geoms_min_max, board_size, len(geoms), complexity_bin_size)

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
    complexity_range = {"c1": range(complexity_min_max["c1"]["min"], complexity_min_max["c1"]["max"] + 1),
                        "c2": range(complexity_min_max["c2"]["min"], complexity_min_max["c2"]["max"] + 1)}

    # Calculate num of configs
    num_configs_per_num_geoms = ((complexity_min_max["c1"]["max"] - complexity_min_max["c1"]["min"] +1) *
                                 (complexity_min_max["c2"]["max"] - complexity_min_max["c2"]["min"] +1) *
                                 complexity_bin_size)
    num_configs_total = (num_geoms_min_max['max']-num_geoms_min_max['min']+1) * num_configs_per_num_geoms

    print(f"Generating {config_id}: {num_configs_total} samples of SlidingGeomPuzzle (SGP) configs for "
          f"{board_size}x{board_size} with {num_geoms_min_max['min']}-{num_geoms_min_max['max']} geoms")

    # Sample initial and goal states until complexity bins are filled with bin size amount of samples
    for i, num_geoms in enumerate(range(num_geoms_min_max['min'], num_geoms_min_max['max']+1)):
        # Track used combinations
        complexity_bins = pd.DataFrame(0, index=complexity_range["c1"], columns=complexity_range["c2"])
        seen_state_combinations = set()
        total_bin_values_checkpoint = 0
        last_checked_time = time.time()  # Initialize the last checked time
        print(f"Start sampling SlidingGeomPuzzle configs for {num_geoms} geoms.")

        while True:
            # Check progress every 'interval' seconds
            if time.time() - last_checked_time >= interval:
                num_configs_current = complexity_bins.sum().sum()
                # Evaluate condition for breaking the loop
                if total_bin_values_checkpoint == num_configs_current:
                    warnings.warn(f"Abort generating further SGP configs, no configs found for {interval} seconds")
                    #break # Break in case you want simulation to stop after a time interval

                print(f"Checking at {datetime.now().strftime('%H:%M')}: {num_configs_current*(i+1)}/{num_configs_total} "
                      f"new configs, checked {len(seen_state_combinations)} total configs")
                total_bin_values_checkpoint = num_configs_current
                last_checked_time = time.time()

            # Sample initial and goal states
            init_state = sample_board_states(num_geoms, board_size)
            goal_state = sample_board_states(num_geoms, board_size)

            # Create a hashable unique combination of init and goal state
            state_combination = (tuple(map(tuple, init_state)), tuple(map(tuple, goal_state)))

            # Calculate cumulative Manhattan distance
            manhattan_heuristic = calculate_manhattan_heuristic(init_state, goal_state)

            # Check if the combination is already seen
            if state_combination in seen_state_combinations:
                continue  # Skip this iteration if already sampled
            else: # Add the combination to the seen set
                seen_state_combinations.add(state_combination)
            if manhattan_heuristic < complexity_min_max["c1"]["min"]-complexity_min_max["c2"]["max"]*2:
                continue
            if manhattan_heuristic > complexity_min_max["c1"]["max"]:
                continue

            print(manhattan_heuristic)
            # Sample geoms without replacement
            geoms_sample = random.sample(geoms, num_geoms)

            # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
            shortest_move_sequence = a_star(board_size, init_state, goal_state)
            random_valid_move_sequence = generate_random_valid_path(board_size, init_state)
            random_invalid_move_sequence = generate_random_invalid_path(board_size, init_state)


            complexity =  {
                "c1": len(shortest_move_sequence)-1,
                "c2": (len(shortest_move_sequence)-1 - manhattan_heuristic)//2
            }

            # Check if the complexity bin is valid
            if complexity['c1'] not in complexity_bins.index or complexity['c2'] not in complexity_bins.columns:
                continue
            elif complexity_bins.loc[complexity['c1'], complexity['c2']] >= complexity_bin_size:
                continue

            # Increment bins based on the flags
            if use_c1_c2[0] and use_c1_c2[1]:  # Both c1 and c2 are used
                complexity_bins.loc[complexity["c1"], complexity["c2"]] += 1
            elif not use_c1_c2[1]:  # Only c1 is used, increment all c2 bins for this c1
                complexity_bins.loc[complexity["c1"], :] += 1
            elif not use_c1_c2[0]:  # Only c2 is used, increment all c1 bins for this c2
                complexity_bins.loc[:, complexity["c2"]] += 1

            bin_fill = complexity_bins.loc[complexity["c1"], complexity["c2"]]

            # Serialize SGP configuration to JSON file
            encode_SGP_config_to_json(board_size, state_combination, geoms_sample,
                                  complexity, bin_fill, shortest_move_sequence,
                                  random_valid_move_sequence, random_invalid_move_sequence,
                                  config_id, config_dir)

            # Check if all bins are full
            if (complexity_bins >= complexity_bin_size).all().all():
                print(f"Successfully finished building all configurations for {num_geoms} geoms")
                break

    return config_id


if __name__ == "__main__":
    # Parameters
    board_size = 5
    num_geoms_min_max = {"min": 12, "max": 12}
    complexity_min_max = {"c1": {"min": 12, "max": 12},  # smallest and highest c1 complexity to be considered
                          "c2": {"min": 0, "max": 0}}  # smallest and highest c2 complexity to be considered
    complexity_bin_size = 1  # amount of puzzle configs per complexity bin
    shapes = ['cube', 'sphere', 'pyramid', 'cylinder', 'cone', 'prism']#, 'cylinder', 'cone', 'prism']
    colors = ['red', 'green', 'blue','yellow', 'purple', 'orange']#, 'yellow', 'purple', 'orange']

    # Generate Sliding Geom Puzzle (SGP) configuration files
    config_id = generate_SGP_configs(board_size=board_size,
                                     num_geoms_min_max=num_geoms_min_max,
                                     complexity_min_max=complexity_min_max,
                                     complexity_bin_size=complexity_bin_size,
                                     shapes=shapes,
                                     colors=colors)
    print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

    # Visualise config stats
    visualise_config_stats(config_id)