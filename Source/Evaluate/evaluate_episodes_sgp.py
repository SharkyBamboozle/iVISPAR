"""
- Main class to evaluate the interactive SGP game
- This class goes through all directories in the experiment folder for experiment_id
- it can be filtered with experiment_signature if only a part should be included e.g. if different games, other than
 SGP are mixed in the same experiment dir
 - The function loads the sim_message_log and the config file to evaluate this episode
 - It goes through a list of different checks, shown as check functions below
 - The results will all be saved into an eval_SGP_ID....json file in the individual episode dirs
"""
import os
import json

import evaluation_utilities as util
from calculate_shortest_path_length import calculate_shortest_path_length


def evaluate_episodes(experiment_id, experiment_signature="InteractivePuzzle"):
    # Set signatures and file paths
    system_json_files_signature = "sim_message_log.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [system_json_files_signature, config_json_files_signature]

    # Get directory and file paths
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Loop over directories
    for sub_dir in sub_dirs:
        file_dict = util.bulk_load_files(sub_dir, file_signatures)
        # Load board size, goal state and current step state
        try:
            with open(file_dict[system_json_files_signature][0], 'r') as system_config_file:
                interaction_log = json.load(system_config_file)
            with open(file_dict[config_json_files_signature][0], 'r') as env_config_file:
                env_config = json.load(env_config_file)
        except Exception as e:
            print(f"Error loading file")

        try:
            move_heuristics = check_shortest_path_length(interaction_log, env_config)

            merged_dict = {
                **move_heuristics,
                **check_min_shortest_path_length(move_heuristics),
                **check_regret(move_heuristics, env_config),
                **check_spl_at_episode_total_shortest_path_length(move_heuristics, env_config),
                **check_normalized_progress(move_heuristics, env_config),
                **check_won(interaction_log, env_config),
                **check_action_validity(interaction_log)
            }
        except Exception as e:
            print(f"Error loading file {sub_dir}")

        # Save the board state as a JSON file
        try:
            episode_eval_json_file_path = os.path.join(sub_dir, f"episode_evaluation.json")
            with open(episode_eval_json_file_path, 'w') as f:
                json.dump(merged_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving board state to {episode_eval_json_file_path}.json: {e}")


def check_shortest_path_length(interaction_log, env_config):
    """
    Calculates the shortest path length for each step in the interaction log.

    Args:
        env_config (dict): Environment configuration containing board size.
        interaction_log (dict): The interaction log with step-by-step states.

    Returns:
        dict: A dictionary containing:
            - 'move_heuristics' (dict):
                - 'values' (list): List of shortest path lengths for each step.
                - 'valid' (bool): True if the calculation was successful, False otherwise.
                - 'error' (str or None): Error message if the calculation fails.
    """
    result = {
        'move_heuristics': {
            'values': [],
            'valid': False,
            'error': None
        }
    }

    try:
        # Get states and board size
        board_size = env_config.get('grid_size')
        step_states = util.extract_all_states_from_config(interaction_log)

        # Ensure there are states to process
        if not step_states:
            result['move_heuristics']['error'] = "No states found in interaction log."
            return result

        goal_state = step_states.pop(0)

        # Loop over each step and calculate heuristic
        for step_state in step_states:
            shortest_move_sequence_length = calculate_shortest_path_length(board_size, step_state, goal_state)
            result['move_heuristics']['values'].append(shortest_move_sequence_length)

        # Mark as valid if successful
        result['move_heuristics']['valid'] = True

    except Exception as e:
        result['move_heuristics']['error'] = str(e)

    return result


def check_min_shortest_path_length(move_heuristics):
    """
    Returns the minimum shortest path length from the dictionary of move heuristics.

    Args:
        move_heuristics (dict): Dictionary containing 'move_heuristics' with 'values', 'valid', and 'error'.

    Returns:
        dict: A dictionary containing:
            - 'min_path' (dict):
                - 'min_path_length' (int or None): The minimum path length, or None if the list is empty.
                - 'valid' (bool): True if a minimum was found, False otherwise.
                - 'error' (str or None): Error message if the operation fails.
    """
    result = {
        'min_path': {
            'min_path_length': None,
            'valid': False,
            'error': None
        }
    }

    try:
        # Extract the list of path lengths from the 'values' key
        move_heuristics_data = move_heuristics.get('move_heuristics', {})
        path_lengths = move_heuristics_data.get('values', [])

        # Check if the list is empty
        if not path_lengths:
            result['min_path']['error'] = "Move heuristics data is empty."
            return result

        # Calculate minimum
        result['min_path']['min_path_length'] = min(path_lengths)
        result['min_path']['valid'] = True

    except Exception as e:
        result['min_path']['error'] = str(e)

    return result


def check_spl_at_episode_total_shortest_path_length(move_heuristics, env_config):
    """
    Returns the shortest path length at the step corresponding to 'complexity_c1' from env_config.

    Args:
        move_heuristics (dict): Dictionary containing 'move_heuristics' sub-dict with 'values', 'valid', 'error'.
        env_config (dict): Environment configuration containing 'complexity_c1' as total path length.

    Returns:
        dict: A dictionary with:
            - 'spl_value' (dict):
                - 'value' (int or None): The shortest path length at the step corresponding to total_spl.
                - 'valid' (bool): True if the value is successfully retrieved, False otherwise.
                - 'error' (str or None): Error message if retrieval fails.
    """
    total_spl = env_config.get('complexity_c1')

    # Initialize return dictionary
    result = {
        'spl_value': {
            'value': None,
            'valid': False,
            'error': None
        }
    }

    try:
        # Extract move_heuristics list and validate
        move_heuristics_data = move_heuristics.get('move_heuristics', {})
        move_heuristics_list = move_heuristics_data.get('values', [])
        valid = move_heuristics_data.get('valid', False)
        error = move_heuristics_data.get('error')

        # Propagate errors if move_heuristics is invalid
        if not valid or not move_heuristics_list:
            result['spl_value']['error'] = error or "Move heuristics data is invalid or empty."
            return result

        # Validate total_spl
        if total_spl is not None:
            # Ensure total_spl is within bounds
            if total_spl < len(move_heuristics_list):
                result['spl_value']['value'] = move_heuristics_list[total_spl]
                result['spl_value']['valid'] = True
            else:
                result['spl_value']['error'] = f"Step {total_spl} out of bounds in move heuristics list."
        else:
            result['spl_value']['error'] = "Total SPL (complexity_c1) is not defined in env_config."

    except Exception as e:
        result['spl_value']['error'] = str(e)

    return result


def check_normalized_progress(move_heuristics, env_config):
    """
    Calculate the normalized progress of the agent at each step as a percentage of the total path.

    Args:
        move_heuristics (dict): Dictionary containing 'move_heuristics' sub-dict with 'values', 'valid', 'error'.
        env_config (dict): Environment configuration containing 'complexity_c1' as total path length.

    Returns:
        dict: Dictionary containing:
            - 'normalized_progress' (dict):
                - 'values' (list): List of normalized progress values (0-100%).
                - 'valid' (bool): True if calculation was successful.
                - 'error' (str or None): Error message if the operation fails.
    """
    result = {
        'normalized_progress': {
            'values': [],
            'valid': False,
            'error': None
        }
    }

    try:
        # Extract move_heuristics list and validate
        move_heuristics_data = move_heuristics.get('move_heuristics', {})
        move_heuristics_list = move_heuristics_data.get('values', [])
        valid = move_heuristics_data.get('valid', False)
        error = move_heuristics_data.get('error')

        # Propagate errors if move_heuristics is invalid
        if not valid or not move_heuristics_list:
            result['normalized_progress']['error'] = error or "Move heuristics data is invalid or empty."
            return result

        # Extract complexity from env_config
        c1_complexity = env_config.get('complexity_c1')

        if c1_complexity is None or c1_complexity == 0:
            result['normalized_progress']['error'] = "Complexity (c1) is missing or zero in environment config."
            return result

        # Calculate normalized progress
        normalized_progress = [
            round(100 * (1 - (value / c1_complexity)), 2)
            if c1_complexity != 0 else 0
            for value in move_heuristics_list
        ]

        # Update result
        result['normalized_progress']['values'] = normalized_progress
        result['normalized_progress']['valid'] = True

    except Exception as e:
        result['normalized_progress']['error'] = str(e)

    return result


def check_won(interaction_log, env_config):
    """
    Checks if the game is completed by examining the 'game_done' flag in the interaction log.
    Verifies if the final state matches the goal state and whether the game was completed optimally.

    Args:
        interaction_log (dict): The interaction log containing step-by-step game progress.
        env_config (dict): Environment configuration containing the optimal shortest path length (complexity_c1).

    Returns:
        dict: A dictionary with:
            - 'won' (bool): True if the game is completed and optimal, False otherwise.
            - 'won_at_spl' (bool): True if the game was completed at the optimal step, False otherwise.
    """
    total_spl = env_config.get('complexity_c1')
    game_won = False
    won_at_spl = False

    # Iterate through all steps in the interaction log
    for step_key, step_data in interaction_log.items():
        step_number = int(step_key.split()[1])  # Extract the step number (e.g., from 'step 0')

        # Check if 'game_done' is True at any step
        if step_data.get('game_done', False):
            # Check if the board state at this step matches the goal state
            board_data = step_data.get('board_data', [])
            all_goal_reached = all(
                item['current_coordinate'] == item['goal_coordinate'] for item in board_data
            )

            if all_goal_reached:
                game_won = True

                # Check if the game was won at the step equal to the optimal path length
                if step_number == total_spl+1: #+1 because start is counted as action
                    won_at_spl = True

    return {
        'won': game_won,
        'won_at_spl': won_at_spl
    }


def check_action_validity(interaction_log):
    """
    Analyzes the interaction log to gather statistics on the validity of actions taken during the episode.

    Args:
        interaction_log (dict): The interaction log containing step-by-step game progress.

    Returns:
        dict: A dictionary with:
            - 'action_validity' (dict):
                - 'validity_counts' (dict): Counts of each validity description.
                - 'total_actions' (int): Total number of actions.
                - 'valid_actions' (int): Count of valid actions.
                - 'invalid_actions' (int): Count of invalid actions.
                - 'error' (str or None): Error message if the operation fails.
    """
    result = {
        'action_validity': {
            'validity_counts': {},
            'total_actions': 0,
            'valid_actions': 0,
            'invalid_actions': 0,
            'error': None
        }
    }

    try:
        # Iterate through each step in the interaction log
        for step_key, step_data in interaction_log.items():
            actions = step_data.get('Actions', [])

            # Iterate through actions and analyze their validity
            for action in actions:
                validity_list = action.get('valididy', [])  # 'valididy' appears to be the key

                for validity in validity_list:
                    # Update overall validity counts
                    result['action_validity']['validity_counts'][validity] = (
                        result['action_validity']['validity_counts'].get(validity, 0) + 1
                    )

                    # Track valid and invalid actions based on descriptions
                    if "valid" in validity.lower():
                        result['action_validity']['valid_actions'] += 1
                    elif "invalid" in validity.lower() or "fail" in validity.lower():
                        result['action_validity']['invalid_actions'] += 1

                    # Count total actions
                    result['action_validity']['total_actions'] += 1

    except Exception as e:
        result['action_validity']['error'] = str(e)

    return result


def check_regret(move_heuristics, env_config):
    """
    Calculate regret based on the difference between the agent's path and the optimal trajectory.

    Args:
        move_heuristics (dict): Dictionary containing 'move_heuristics' sub-dict with 'values', 'valid', 'error'.
        env_config (dict): Environment configuration containing 'complexity_c1' as total path length.

    Returns:
        dict: Dictionary containing:
            - 'regret' (dict):
                - 'values' (list): Cumulative regret values per step.
                - 'valid' (bool): True if calculation was successful.
                - 'error' (str or None): Error message if the operation fails.
    """
    result = {
        'regret': {
            'values': [],
            'valid': False,
            'error': None
        }
    }

    try:
        # Extract necessary data from the nested structure
        move_heuristics_data = move_heuristics.get('move_heuristics', {})
        move_heuristics_list = move_heuristics_data.get('values', [])
        valid = move_heuristics_data.get('valid', False)
        error = move_heuristics_data.get('error')

        # If move_heuristics itself is invalid, pass the error along
        if not valid or not move_heuristics_list:
            result['regret']['error'] = error or "Move heuristics data is invalid or empty."
            return result

        c1_complexity = env_config.get('complexity_c1')

        if c1_complexity is None:
            result['regret']['error'] = "Complexity (c1) missing in environment config."
            return result

        # Initialize regret list
        regret = []
        agent_reached_zero = False  # Track if the agent's heuristic has reached zero

        # Calculate regret per step
        for step in range(len(move_heuristics_list)):
            optimal_value = c1_complexity - step
            agent_value = move_heuristics_list[step]

            # If the agent already reached 0, keep the last regret
            if agent_reached_zero:
                regret.append(regret[-1])
            else:
                # Calculate the regret as the difference between agent and optimal value
                step_regret = agent_value - optimal_value
                regret.append(step_regret)

                # Track if agent value reaches zero
                if agent_value == 0:
                    agent_reached_zero = True

        # Update result
        result['regret']['values'] = regret
        result['regret']['valid'] = True

    except Exception as e:
        result['regret']['error'] = str(e)

    return result


if __name__ == "__main__":

    experiment_id = 'Qwen_text'
    experiment_signature = "InteractivePuzzle"

    # Evaluate and plot for each episode of the experiment
    evaluate_episodes(experiment_id, experiment_signature=experiment_signature)
