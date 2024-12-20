import os
import json
import numpy as np
import pandas as pd
import shutil


def copy_and_episodes(experiment_id_1, experiment_id_2, add_identifier="", experiment_signature="InteractivePuzzle"):
    """
    Copies subdirectories from one experiment directory to another and appends an identifier
    to the subdirectory names after the experiment signature.

    Args:
        experiment_id_1 (str): The source experiment ID.
        experiment_id_2 (str): The destination experiment ID.
        add_identifier (str): The identifier to add after the experiment signature in the directory name.
        experiment_signature (str): The signature used to identify episode directories.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    src_experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id_1)
    dest_experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id_2)

    # Ensure destination directory exists
    os.makedirs(dest_experiment_dir, exist_ok=True)

    # Filter subdirectories that match the signature (full paths are already returned)
    sub_dirs = filter_experiment_sub_dirs(src_experiment_dir, experiment_signature=experiment_signature)

    for src_sub_dir_path in sub_dirs:
        # Extract the original folder name from the path
        original_folder_name = os.path.basename(src_sub_dir_path)

        # Insert the identifier after the experiment signature in the directory name
        if f"_{experiment_signature}_" in original_folder_name:
            modified_folder_name = original_folder_name.replace(
                f"_{experiment_signature}_",
                f"_{experiment_signature}_{add_identifier}_"
            )
        else:
            # If the experiment signature is not in the folder name, just add the identifier at the end
            modified_folder_name = f"{original_folder_name}_{add_identifier}"

        dest_sub_dir_path = os.path.join(dest_experiment_dir, modified_folder_name)

        try:
            shutil.copytree(src_sub_dir_path, dest_sub_dir_path)
            print(f"Copied {src_sub_dir_path} to {dest_sub_dir_path}")
        except Exception as e:
            print(f"Error copying {src_sub_dir_path} to {dest_sub_dir_path}: {e}")



def clean_and_process_pd_frame(experiment_id):
    """
    Cleans and processes the a_star_heuristic.csv file for an experiment.
    Ensures all episodes are 20 steps long and sets all subsequent steps to 0
    if any agent reaches 0 at any step in an episode.

    Args:
        experiment_id (str): The experiment identifier.
    """
    # Define the base and results directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)

    # Path to the CSV file
    csv_path = os.path.join(results_dir, 'a_star_heuristic.csv')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Define the maximum episode length
    max_steps = 20

    # Get the list of agent columns (excluding 'episode_nr' and 'episode_step')
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Pad the episodes to ensure each episode has 20 steps
    complete_episodes = []
    for episode_nr, group in df.groupby('episode_nr'):
        # Create a DataFrame with steps 0 to max_steps-1
        episode_df = pd.DataFrame({'episode_step': range(max_steps)})
        episode_df['episode_nr'] = episode_nr

        # Merge the existing episode with the full 0-19 step range, filling missing values with 0
        merged_df = pd.merge(episode_df, group, on=['episode_nr', 'episode_step'], how='left')

        # Fill NaN values with 0 for the agent columns
        merged_df[agent_columns] = merged_df[agent_columns].fillna(0)

        # Ensure that after an agent hits 0, all subsequent steps remain 0
        for agent in agent_columns:
            zero_hit = False
            for i in range(len(merged_df)):
                if merged_df.loc[i, agent] == 0:
                    zero_hit = True
                if zero_hit:
                    merged_df.loc[i, agent] = 0

        complete_episodes.append(merged_df)

    # Concatenate all processed episodes back into a single DataFrame
    cleaned_df = pd.concat(complete_episodes, ignore_index=True)

    # Save the cleaned DataFrame as a CSV file
    cleaned_csv_path = os.path.join(results_dir, 'cleaned_a_star_heuristic.csv')
    cleaned_df.to_csv(cleaned_csv_path, index=False)
    print(f"Cleaned data saved to {cleaned_csv_path}")

def clean_and_process_normalized_progress(experiment_id):
    """
    Cleans and processes the normalized_progress.csv file for an experiment.
    Ensures all episodes are 20 steps long and sets all subsequent steps to 100%
    if any agent reaches 100% at any step in an episode.

    Args:
        experiment_id (str): The experiment identifier.
    """
    # Define the base and results directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)

    # Path to the CSV file
    csv_path = os.path.join(results_dir, 'normalized_progress.csv')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Define the maximum episode length
    max_steps = 20

    # Get the list of agent columns (excluding 'episode_nr' and 'episode_step')
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Pad the episodes to ensure each episode has 20 steps
    complete_episodes = []
    for episode_nr, group in df.groupby('episode_nr'):
        # Create a DataFrame with steps 0 to max_steps-1
        episode_df = pd.DataFrame({'episode_step': range(max_steps)})
        episode_df['episode_nr'] = episode_nr

        # Merge the existing episode with the full 0-19 step range, filling missing values with 100
        merged_df = pd.merge(episode_df, group, on=['episode_nr', 'episode_step'], how='left')

        # Fill NaN values with 100 for the agent columns (since missing steps after 100% should be 100)
        merged_df[agent_columns] = merged_df[agent_columns].fillna(100)

        # Ensure that after an agent hits 100%, all subsequent steps remain 100%
        for agent in agent_columns:
            reached_100 = False
            for i in range(len(merged_df)):
                if merged_df.loc[i, agent] == 100:
                    reached_100 = True
                if reached_100:
                    merged_df.loc[i, agent] = 100

        complete_episodes.append(merged_df)

    # Concatenate all processed episodes back into a single DataFrame
    cleaned_df = pd.concat(complete_episodes, ignore_index=True)

    # Save the cleaned DataFrame as a CSV file
    cleaned_csv_path = os.path.join(results_dir, 'cleaned_normalized_progress.csv')
    cleaned_df.to_csv(cleaned_csv_path, index=False)
    print(f"Cleaned data saved to {cleaned_csv_path}")


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
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)

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




if __name__ == "__main__":
    copy_and_episodes("experiment_ID_20241219_222228_Gemini_l", "evaluate_Berkeley", add_identifier="Gemini_vision", experiment_signature="InteractivePuzzle")