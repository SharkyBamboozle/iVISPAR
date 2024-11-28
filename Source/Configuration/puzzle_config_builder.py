# Import statements
import os
import random
import numpy as np
import json
import time
from datetime import datetime

from puzzle_config_complexity import a_star, manhattan_heuristic
from puzzle_config_visualizer import visualize_config_stats


def convert_to_landmarks(init_state, goal_state, geoms):
    # Prepare the landmarks list
    landmarks = []
    for geom_nr, (start, goal, (body, color)) in enumerate(zip(init_state, goal_state, geoms), start=1):
        landmark = {
            "geom_nr": geom_nr,
            "body": body,
            "color": color,
            "start_coordinate": [int(x) for x in start],  # Convert each element to native Python int             #try np.array([[1, 0], [2, 1]], dtype=np.int32).tolist()
            "goal_coordinate": [int(x) for x in goal]  # Convert each element to native Python int
        }
        landmarks.append(landmark)

    # Return the JSON structure
    return landmarks


def build_SGP_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, geoms, config_id, config_dir):

    # Initialize bins
    complexity_bins = {c: 0 for c in range(complexity_min_max[0], complexity_min_max[1] + 1)}
    total_bin_values = sum(complexity_bins.values())


    # Track used combinations
    seen_state_combinations = set()

    # Sample board states
    sample_board_states = lambda num_geoms: np.stack((
        (idx := np.random.choice(board_size ** 2, num_geoms, replace=False)) // board_size,
        idx % board_size), axis=1)


    # Timer settings
    start_time = time.time()  # Start the timer
    interval = 300  # 5 minutes
    last_checked_time = time.time()  # Initialize the last checked time

    # Sample initial and goal states until complexity bins are filled with bin size amount of samples
    #while True:
    for i in range(100*1000):

        # Sample initial and goal states
        init_state = sample_board_states(num_geoms)
        goal_state = sample_board_states(num_geoms)

        # Create a unique combination of init and goal state
        state_combination = (str(init_state), str(goal_state))

        # Check if the combination is already seen
        if state_combination in seen_state_combinations:
            continue  # Skip this iteration if already sampled
        else: # Add the combination to the seen set
            seen_state_combinations.add(state_combination)

        # Sample geoms without replacement
        geoms_sample = random.sample(geoms, num_geoms)

        # Measure complexity in form of shortest sequence length and cumulative Manhattan distance
        shortest_move_sequence = a_star(board_size, init_state, goal_state)
        cumulative_Manhattan_distance = manhattan_heuristic(init_state, goal_state)

        # Complexity measures
        complexity_first_order = len(shortest_move_sequence)-1
        complexity_second_order = complexity_first_order - cumulative_Manhattan_distance

        # Check if the complexity bin is valid
        if (complexity_first_order not in complexity_bins
                or complexity_bins[complexity_first_order] >= complexity_bin_size):
            print(f"complexity {complexity_first_order} not in bins")
            continue

        # Increment the corresponding bin
        complexity_bins[complexity_first_order] += 1

        # Save as JSON
        config_instance_id = (f"SGP_config_ID_{config_id}_c1_{complexity_first_order}"
                              f"c1_{complexity_second_order}_i_{complexity_bins[complexity_first_order]}")

        landmarks_json = convert_to_landmarks(init_state, goal_state, geoms_sample)

        # Structure the output for JSON
        json_output = {
            "config_instance_id": config_instance_id,
            "experiment_type": "SGP",
            "grid_size": board_size,
            "landmarks": landmarks_json,
            "complexity_first_order": complexity_first_order,
            "complexity_second_order": complexity_second_order,
            "shortest_move_sequence": shortest_move_sequence
        }

        # Save the configuration to a JSON file
        json_filename = os.path.join(config_dir, f"{config_instance_id}.json")
        with open(json_filename, 'w') as json_file:
            json.dump(json_output, json_file, indent=4)


        # End the timer and calculate elapsed time
        if time.time() - last_checked_time >= interval:  # Check if 5 minutes have passed
            print(f"Checking at 5-minute interval: {i}")
            visualize_config_stats(config_dir)

            # Evaluate condition for breaking the loop
            if total_bin_values == sum(complexity_bins.values()):
                break
            else:
                total_bin_values = sum(complexity_bins.values())

            # Reset last checked time
            last_checked_time =  time.time()


        # Check if all bins are full
        if all(complexity_bins[c] >= complexity_bin_size for c in complexity_bins):
            print("Finished building all configurations")
            break