"""
Duplicate for fix_dir_name
replace later with cross-directory imports
"""

import os
import json
import numpy as np
import pandas as pd


def make_results_dir(experiment_id):
    # Set up paths for experiment directory and results directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)
    return  experiment_dir, results_dir


def filter_experiment_sub_dirs(experiment_id, experiment_signature):
    """
    Filters and returns all subdirectories within the experiment directory
    that contain the specified signature in their names.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): The signature to search for in subdirectory names.

    Returns:
        list: A list of subdirectory paths containing the specified signature in their names.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id, 'Episodes')

    # Ensure the experiment directory exists
    if not os.path.exists(experiment_dir):
        #TODO raise error
        return []

    # Get all subdirectories containing the signature
    sub_dirs = [
        os.path.join(experiment_dir, subdir) for subdir in os.listdir(experiment_dir)
        if os.path.isdir(os.path.join(experiment_dir, subdir)) and experiment_signature in subdir
    ]

    return sub_dirs



def bulk_load_files(dir_path, file_signatures):
    """
    Loads all files from the provided directory path that match any of the given file signatures.
    File signatures can include partial start and end patterns like 'config_ID_' or '.json'.

    Args:
        dir_path (str): The directory path to search for files.
        file_signatures (list): A list of file signature patterns. Each pattern can be
                                a partial start or end of a filename (e.g., 'config_ID_*' or '*.json').

    Returns:
        dict: A dictionary where keys are file signatures and values are lists of matching file paths.
    """
    file_dict = {sig: [] for sig in file_signatures}

    # Ensure the directory exists
    if not os.path.exists(dir_path):
        print(f"Directory {dir_path} does not exist.")
        return file_dict

    # Get all files in the directory
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        # Check if this is a file (not a directory)
        if os.path.isfile(file_path):
            # Check if the file matches any of the file signatures
            for sig in file_signatures:
                if file_name.startswith(sig.split('*')[0]) and file_name.endswith(sig.split('*')[-1]):
                    file_dict[sig].append(file_path)

    return file_dict


def extract_all_states_from_config(json_config):
    """
    Extracts all current states from the board data in the JSON configuration for all steps.

    Args:
        json_config (dict): The JSON configuration containing steps with 'board_data'.

    Returns:
        list: A list of 2D NumPy arrays, where each array represents the current state
              of the board for each step.
    """
    all_states = []

    for step_key, step_data in json_config.items():
        board_data = step_data.get("board_data", [])

        if not board_data:
            raise ValueError(f"No 'board_data' found for {step_key} in the JSON config.")

        # Extract the current coordinates from each item in board_data
        state = [item["current_coordinate"] for item in board_data]

        # Convert to NumPy array and append to the list of all states
        state_array = np.array(state, dtype=int)
        all_states.append(state_array)

    return all_states


def compile_episode_data_to_data_frame(experiment_id, experiment_signature, episode_data_file):
    """
    Compiles episode data from multiple subdirectories into a single DataFrame.

    Args:
        experiment_id (str): The ID of the experiment.
        experiment_signature (str): Signature to filter relevant subdirectories.

    Returns:
        pd.DataFrame: The DataFrame containing the compiled data.
    """
    # Directories
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Container for all move heuristic values
    all_episode_data = []

    max_length = 0  # To track the maximum step count for padding

    # Loop over directories
    for sub_dir in sub_dirs:
        try:
            file_path = os.path.join(sub_dir, episode_data_file)
            with open(file_path, 'r') as file:
                move_heuristics = json.load(file)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            continue  # Skip this subdirectory if there is an error

        # Check if move_heuristics is valid
        if not isinstance(move_heuristics, list):
            print(f"Invalid data in {file_path}: not a list")
            continue

        # Update the max length to ensure all episodes have the same length
        max_length = max(max_length, len(move_heuristics))

        # Add the current episode's move heuristics to the container
        all_episode_data.append(move_heuristics)

    # Pad all rows with 0s to match the maximum length
    padded_data = [row + [0] * (max_length - len(row)) for row in all_episode_data]

    # Create a DataFrame where each row corresponds to an episode
    df = pd.DataFrame(padded_data)

    return df
