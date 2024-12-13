import json
import os
import math
import numpy as np
import zlib
import hashlib
import pickle


def load_params_from_json(file_name):
    """
    Loads parameters from a JSON file and returns them as a dictionary.

    Args:
        file_path (str): Path to the JSON file containing the parameters.

    Returns:
        dict: A dictionary containing all the parameters from the JSON file.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(base_dir, 'Data', 'Params', file_name)
    try:
        with open(file_path, 'r') as file:
            params = json.load(file)
        print(f"Loaded parameters from {file_path} successfully.")
        return params
    except Exception as e:
        print(f"Error loading parameters from {file_path}: {e}")
        return {}


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


def get_md5_hash(state_combination):
    """Convert the state string to an MD5 hash."""
    state_data = pickle.dumps(state_combination)
    return hashlib.md5(state_data).hexdigest()


def compress_with_zlib(state_combination):
    """Compress the state combination using zlib."""
    state_data = pickle.dumps(state_combination)
    return zlib.compress(state_data)