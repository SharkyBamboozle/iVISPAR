# Import statements
import os
import json
import numpy as np


def get_tile_color(tile_index, board_size):
    """
    Determines the color of a tile based on its position in the goal state layout.
    Args:
        tile_index (int): The index of the tile in the goal state (0-based).
        board_size (int): The size of the board (n x n).
    Returns:
        str: The color assigned to the tile ("green", "red", or "blue").
    """
    # Get the total number of tiles on the board
    total_tiles = board_size ** 2

    # Reshape the goal state indices to match a 2D board layout
    goal_indices = np.arange(total_tiles).reshape((board_size, board_size))

    # Calculate the position of the tile (row, col) from its index
    row, col = np.where(goal_indices == tile_index)
    row, col = row[0], col[0]

    # Calculate the "depth" of the current tile (how far it is from the edge)
    depth = min(row, col, board_size - 1 - row, board_size - 1 - col)

    if board_size == 3:
        # For a 3x3 board, all tiles except the center are green
        if tile_index == 4:  # Center tile
            return "red"
        else:
            return "green"

    elif board_size == 4:
        # For a 4x4 board, all tiles on the outer ring are green, and inner 2x2 are red
        if 1 <= row <= 2 and 1 <= col <= 2:
            return "red"
        else:
            return "green"

    elif board_size == 5:
        # For a 5x5 board, outer ring is green, middle ring is red, and center is blue
        if depth == 0:  # Outer ring
            return "green"
        elif depth == 1:  # Middle ring
            return "red"
        else:  # Center tile
            return "blue"

    else:
        # Generalize for larger boards
        if depth == 0:  # Outer ring
            return "green"
        elif depth == (board_size // 2):  # Center tile for odd-sized boards
            return "blue"
        elif depth <= (board_size // 2) - 1:  # Rings closer to the center
            return "red"
        else:
            return "green"


def translate_moves_to_commands(shortest_move_sequence, landmarks):
    """
    Translates the shortest move sequence into text commands.

    Parameters:
        shortest_move_sequence (list): A 3D list representing the board states for all tiles/objects.
        landmarks (list): A list of dictionaries describing the landmarks with geom_nr, body, and color.

    Returns:
        list: A list of text commands for the moves.
    """
    directions = {
        (-1, 0): "left",    # Decrease in row index
        (1, 0): "right",    # Increase in row index
        (0, -1): "down",    # Decrease in column index
        (0, 1): "up"        # Increase in column index
    }

    commands = ["start"]
    num_steps = len(shortest_move_sequence)

    # Determine the move format by checking if "tile" appears as the 'body' for any landmark
    move_format = "tiles" if all(l["body"] == "tile" for l in landmarks) else "geoms"

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

                    if move_format == "geoms":
                        # Use the 'color' and 'body' information from the landmark
                        command = f"move {landmark['color']} {landmark['body']} {direction}"
                    elif move_format == "tiles":
                        # Use the 'geom_nr' as the identifier for the tile number
                        command = f"move tile {geom_nr} {direction}"
                    else:
                        raise ValueError(f"Invalid move_format: {move_format}. Must be 'geoms' or 'tiles'.")

                    commands.append(command)

    #commands.append("done")
    return commands



def encode_SGP_config_to_json(board_size, state_combination, geoms_sample,
                          complexity, bin_fill, shortest_move_sequence,
                          random_valid_move_sequence, random_invalid_move_sequence,
                          config_id, config_dir):

    config_instance_id = (f"{config_id}_b_{board_size}_g_{len(geoms_sample)}_c1_{complexity['c1']}_c2_{complexity['c2']}"
                          f"_i_{bin_fill}")


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
        "experiment_type": "SlidingGeomPuzzle",
        "complexity_c1": complexity['c1'],
        "complexity_c2": complexity['c2'],
        "grid_size": board_size,
        "landmarks": landmarks,
        "use_rendering": True,
        "shortest_move_sequence": translate_moves_to_commands(shortest_move_sequence, landmarks),
        'random_valid_move_sequence': translate_moves_to_commands(random_valid_move_sequence, landmarks),
        'random_invalid_move_sequence': translate_moves_to_commands(random_invalid_move_sequence, landmarks),
    }

    # Save the configuration to a JSON file
    json_filename = os.path.join(config_dir, f"config_{config_instance_id}.json")
    with open(json_filename, 'w') as json_file:
        json.dump(json_output, json_file, indent=4)



def encode_STP_config_to_json(board_size, state_combination, complexity, bin_fill, shortest_move_sequence,
                              random_valid_move_sequence, random_invalid_move_sequence, config_id, config_dir):
    """
    Encodes the configuration for the sliding tile puzzle (STP) and saves it as a JSON file.

    Args:
        board_size (int): The size of the board (n x n).
        state_combination (tuple): A tuple of (initial state, goal state) for the tiles.
        complexity (dict): Complexity metrics for the configuration.
        bin_fill (int): The fill status of the bin for this complexity level.
        shortest_move_sequence (list): Optimal move sequence for the puzzle.
        random_valid_move_sequence (list): Random move sequence with valid moves.
        random_invalid_move_sequence (list): Random move sequence with invalid moves.
        config_id (str): The identifier for this configuration.
        config_dir (str): The directory where the JSON file will be saved.
    """
    config_instance_id = (f"{config_id}_b_{board_size}_g_{len(state_combination)}_c1_{complexity['c1']}_i_{bin_fill}")
    landmarks = []

    for tile_nr, (start, goal) in enumerate(zip(state_combination[0], state_combination[1]), start=0):  # Changed start=1 to start=0
        color = get_tile_color(tile_nr, board_size)
        landmark = {
            "geom_nr": tile_nr + 1,  # Starts from 1 for human-readable geom numbers
            "body": "tile",  # Fixed shape
            "color": color,  # Set color based on position in the goal state
            "start_coordinate": [int(x) for x in start],  # Convert each element to native Python int
            "goal_coordinate": [int(x) for x in goal]  # Convert each element to native Python int
        }
        landmarks.append(landmark)

    # Structure the output for JSON
    json_output = {
        "config_instance_id": config_instance_id,
        "experiment_type": "SlidingGeomPuzzle",
        "complexity_c1": complexity['c1'],
        "grid_size": board_size,
        "landmarks": landmarks,
        "shortest_move_sequence": translate_moves_to_commands(shortest_move_sequence, landmarks),
        'random_valid_move_sequence': translate_moves_to_commands(random_valid_move_sequence, landmarks),
        'random_invalid_move_sequence': translate_moves_to_commands(random_invalid_move_sequence, landmarks),
    }

    # Save the configuration to a JSON file
    json_filename = os.path.join(config_dir, f"config_{config_instance_id}.json")
    with open(json_filename, 'w') as json_file:
        json.dump(json_output, json_file, indent=4)
