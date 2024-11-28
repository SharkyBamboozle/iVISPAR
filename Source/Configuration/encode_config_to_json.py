# Import statements
import os
import json


def translate_moves_to_commands(shortest_move_sequence, landmarks):
    """
    Translates the shortest move sequence into text commands.

    Parameters:
        shortest_move_sequence (list): A 3D list representing the board states for all geoms.
        landmarks (list): A list of dictionaries describing the landmarks with geom_nr, body, and color.

    Returns:
        list: A list of text commands for the moves.
    """
    directions = {
        (-1, 0): "up",     # Decrease in row index
        (1, 0): "down",    # Increase in row index
        (0, -1): "left",   # Decrease in column index
        (0, 1): "right"    # Increase in column index
    }

    commands = []
    num_steps = len(shortest_move_sequence)

    # Iterate through each step (state transitions) in the shortest move sequence
    for step in range(num_steps - 1):  # Last state is the goal state, no moves after that
        current_state = shortest_move_sequence[step]
        next_state = shortest_move_sequence[step + 1]

        # Iterate through all geoms and their movements
        for geom_nr, (current_pos, next_pos) in enumerate(zip(current_state, next_state), start=1):
            if current_pos != next_pos:  # If the position has changed
                # Calculate the direction of movement
                delta = (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])
                direction = directions.get(delta)

                if direction:
                    # Find the corresponding landmark for geom_nr
                    landmark = next(l for l in landmarks if l["geom_nr"] == geom_nr)
                    command = f"move {landmark['color']} {landmark['body']} {direction}"
                    commands.append(command)

    return commands


def encode_config_to_json(board_size, state_combination, geoms_sample,
                          complexity, complexity_bins, shortest_move_sequence,
                          config_id, config_dir):

    config_instance_id = (f"{config_id}_c1_{complexity['c1']}_c2_{complexity['c2']}"
                          f"_i_{complexity_bins[complexity['c1']][complexity['c2']]}")


    landmarks = []
    for geom_nr, (start, goal, (body, color)) in enumerate(zip(state_combination[0], state_combination[1], geoms_sample), start=1):
        landmark = {
            "geom_nr": geom_nr,
            "body": body,
            "color": color,
            "start_coordinate": [int(x) for x in start],  # Convert each element to native Python int             #try np.array([[1, 0], [2, 1]], dtype=np.int32).tolist()
            "goal_coordinate": [int(x) for x in goal]  # Convert each element to native Python int
        }
        landmarks.append(landmark)

    # Structure the output for JSON
    json_output = {
        "config_instance_id": config_instance_id,
        "experiment_type": "SGP",
        "complexity_c1": complexity['c1'],
        "complexity_c2": complexity['c2'],
        "grid_size": board_size,
        "landmarks": landmarks,
        "shortest_move_sequence": translate_moves_to_commands(shortest_move_sequence, landmarks)
    }

    # Save the configuration to a JSON file
    json_filename = os.path.join(config_dir, f"{config_instance_id}.json")
    with open(json_filename, 'w') as json_file:
        json.dump(json_output, json_file, indent=4)