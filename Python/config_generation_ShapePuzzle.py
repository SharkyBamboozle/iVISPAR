import os
import json
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import warnings


def _generate_setup_id():
    """Generate the setup ID based on current date and time."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _generate_unique_landmarks(n, board_size):
    """
    Generate n unique landmarks with body, color, and coordinate properties.

    - Each landmark must have a unique combination of shape (body) and color.
    - Coordinates must be unique for all landmarks.

    Args:
        n (int): The number of unique landmarks to generate.
        board_size (int): The size of the grid (grid_size x grid_size).

    Returns:
        List[dict]: A list of unique landmarks.
    """
    bodies = ['cube', 'ball', 'pyramid']
    colors = ['red', 'green', 'blue']

    # To track unique combinations of body + color
    used_combinations = set()

    # To track unique coordinates
    used_coordinates = set()

    landmarks = []

    while len(landmarks) < n:
        body = random.choice(bodies)
        color = random.choice(colors)
        coordinate = (random.randint(0, board_size - 1), random.randint(0, board_size - 1))  # Random grid coordinates

        # Check if the combination of body and color is unique
        combination = (body, color)
        if combination in used_combinations:
            continue  # Skip if this body-color combination is already used

        # Ensure the coordinates are unique as well
        if coordinate in used_coordinates:
            continue  # Skip if the coordinate is already taken

        # If both checks pass, add the landmark
        new_landmark = {'body': body, 'color': color, 'coordinate': coordinate}

        # Mark the combination and coordinate as used
        used_combinations.add(combination)
        used_coordinates.add(coordinate)

        landmarks.append(new_landmark)

    return landmarks


def _visualize_landmarks(landmarks, board_size, filename):
    """
    Visualize the grid with landmarks using matplotlib.

    Args:
        landmarks (list): List of landmarks with their properties.
        board_size (int): Size of the grid (grid_size x grid_size).
        filename (str): save the plot to this file.
    """
    fig, ax = plt.subplots(figsize=(board_size, board_size))

    # Create a grid
    for x in range(board_size):
        for y in range(board_size):
            ax.add_patch(Rectangle((x, y), 1, 1, edgecolor='black', facecolor='white'))

    # Plot the landmarks
    for landmark in landmarks:
        x, y = landmark['coordinate']
        color = landmark['color']

        if landmark['body'] == 'cube':
            ax.add_patch(Rectangle((x, y), 1, 1, color=color, alpha=0.6))
        elif landmark['body'] == 'ball':
            ax.add_patch(Circle((x + 0.5, y + 0.5), 0.5, color=color, alpha=0.6))
        elif landmark['body'] == 'pyramid':
            ax.add_patch(Polygon([[x + 0.5, y + 1], [x, y], [x + 1, y]], color=color, alpha=0.6))

    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    # Save the plot
    plt.savefig(filename)


def _generate_ShapePuzzle_config(board_size=3, num_landmarks=3):
    """
    Generate a single ShapePuzzle configuration.

    Args:
        board_size (int): The size of the board (board_size x board_size).
                          Must be at least 2 to have enough space for landmarks and moves.
        num_landmarks (int): The number of landmarks to generate. Must be between 1 and 9,
                             and there must be enough free space on the board for at least one empty space.
                             If a value outside this range is provided, it will be adjusted
                             and a warning will be issued.

    Returns:
        dict: Contains the list of landmarks and the board size.
    """
    # Ensure num_landmarks is between 1 and 9, with warnings for out-of-bounds values
    if num_landmarks < 1 or num_landmarks > 9:
        warnings.warn(f"Number of landmarks out of range, setting to {max(1, min(num_landmarks, 9))}.")
    num_landmarks = max(1, min(num_landmarks, 9))

    # Ensure the number of fields (board_size x board_size) is at least num_landmarks + 1 and board_size >= 2
    if board_size < 2 or board_size * board_size <= num_landmarks:
        warnings.warn(f"Not enough space for {num_landmarks} landmarks, increasing board size.")
        # Adjust the board_size to be large enough for num_landmarks + 1 fields
        board_size = (num_landmarks + 1) ** 0.5
        board_size = int(board_size) + (1 if board_size % 1 > 0 else 0)  # Ensure board_size is an integer

    ShapePuzzle_config = _generate_unique_landmarks(num_landmarks, board_size)

    return {'board_size': board_size, 'ShapePuzzle': ShapePuzzle_config}


def generate_ShapePuzzle_configs(num_configs, board_size=3, num_landmarks=3):
    """
    Generate multiple ShapePuzzle configurations and save them to a unique directory.

    Args:
        num_configs (int): The number of configurations to generate.
        board_size (int): The size of the board for each configuration.
        num_landmarks (int): The number of landmarks for each configuration.

    Returns:
        str: The path to the directory where the configurations are saved.
    """
    # Generate a unique ID for this set of configurations
    generation_id = _generate_setup_id()

    # Define the path one level up from the current directory (source code directory)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Create the game_configs directory in the parent directory if it doesn't exist
    config_root_dir = os.path.join(base_dir, 'game_configs')
    if not os.path.exists(config_root_dir):
        os.makedirs(config_root_dir)

    # Create a unique subdirectory for this generation of configurations
    config_dir = os.path.join(config_root_dir, f"ShapePuzzle_ID_{generation_id}")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Loop to generate multiple configurations
    for i in range(num_configs):
        # Generate a single configuration
        config = _generate_ShapePuzzle_config(board_size, num_landmarks)

        # Generate an experiment ID based on the file name (incremental)
        experiment_id = f"ShapePuzzle_config_ID_{generation_id}_{i+1}"

        # Structure the config for JSON output to match the original format
        json_output = {
            "experiment_id": experiment_id,
            "grid_size": config['board_size'],  # Rename board_size to grid_size in the JSON
            "landmarks": config['ShapePuzzle']  # Rename ShapePuzzle to landmarks in the JSON
        }

        # Save each configuration to a JSON file
        json_filename = os.path.join(config_dir, f"{experiment_id}.json")
        with open(json_filename, 'w') as json_file:
            json.dump(json_output, json_file, indent=4)

        # Save the plot as a PNG file
        plot_filename = os.path.join(config_dir, f"ShapePuzzle_config_ID_{generation_id}_{i+1}.png")
        _visualize_landmarks(config['ShapePuzzle'], config['board_size'], filename=plot_filename)

    print(f"ShapePuzzle configs generated to {config_dir}")

    # Return the path to the directory where all configurations were saved
    return config_dir

if __name__ == "__main__":
    # Generate ShapePuzzle configuration
    path = generate_ShapePuzzle_configs(num_configs=5, board_size=3, num_landmarks=3)
