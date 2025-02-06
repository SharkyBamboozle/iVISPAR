"""Generate Sliding Geom Puzzle (SGP) configuration files"""

# Import statements
import os
import random
import pandas as pd
import time
import warnings
from datetime import datetime

from find_shortest_move_sequence import a_star, calculate_manhattan_heuristic
from encode_config_to_json import encode_SGP_config_to_json
from find_random_move_sequence import generate_random_valid_path, generate_random_invalid_path
import configuration_utilities as util


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
    util.validate_parameters(complexity_min_max, num_geoms_min_max, board_size, len(geoms), complexity_bin_size)

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

                print(f"Checking at {datetime.now().strftime('%H:%M')}: {num_configs_current * (i + 1)}/{num_configs_total} "
                      f"new configs, checked {len(seen_state_combinations):,} total configs")

                total_bin_values_checkpoint = num_configs_current
                last_checked_time = time.time()

            # Sample initial and goal states
            init_state = util.sample_board_states(num_geoms, board_size)
            goal_state = util.sample_board_states(num_geoms, board_size)

            # Create a hashable unique combination of init and goal state
            state_combination = (tuple(map(tuple, init_state)), tuple(map(tuple, goal_state)))

            # Compress the state combination using zlib
            compressed_state_combination = util.compress_with_zlib(state_combination)

            # Check if the combination is already seen
            if compressed_state_combination  in seen_state_combinations:
                continue  # Skip this iteration if already sampled
            else: # Add the combination to the seen set
                seen_state_combinations.add(state_combination)

            # Calculate cumulative Manhattan distance
            manhattan_heuristic = calculate_manhattan_heuristic(init_state, goal_state)
            if manhattan_heuristic < complexity_min_max["c1"]["min"]-complexity_min_max["c2"]["max"]*2:
                continue
            if manhattan_heuristic > complexity_min_max["c1"]["max"]:
                continue

            # Sample geoms without replacement
            geoms_sample = random.sample(geoms, num_geoms)

            # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
            shortest_move_sequence = a_star(board_size, init_state, goal_state, max_depth=complexity_min_max["c1"]["max"])
            if shortest_move_sequence == None:
                continue

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

            random_valid_move_sequence = generate_random_valid_path(board_size, init_state)
            random_invalid_move_sequence = generate_random_invalid_path(board_size, init_state)

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
    # Load parameters from the JSON file
    params = util.load_params_from_json('params_SGP_config_ICML.json')

    # Generate Sliding Geom Puzzle (SGP) configuration files
    config_id = generate_SGP_configs(board_size=params.get('board_size', 5),
                                     num_geoms_min_max=params.get('num_geoms_min_max', {"min": 8, "max": 8}),
                                     complexity_min_max=params.get('complexity_min_max', {"c1": {"min": 16, "max": 16},
                                                                                          "c2": {"min": 0, "max": 0}}),
                                     complexity_bin_size= params.get('complexity_bin_size', 1),
                                     shapes=params.get('shapes', ['sphere', 'cylinder', 'cone']),
                                     colors=params.get('colors', ['red', 'green', 'blue']))
    print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")