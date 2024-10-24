import os
import shutil
import subprocess
import time
import csv
from datetime import datetime

class UserInteractiveAgent:
    """
    A simple interactive agent that simulates the role of an LLM for user interaction.

    Instead of generating responses automatically, it prompts the user for manual input
    and returns that input as the action.
    """

    def act(self, observation):
        """
        Simulates the process of responding to an observation by asking for user input.

        Args:
            observation (str): A placeholder for the environment's observation. It is not used
                               for decision-making in this class, but passed for compatibility
                               with LLM-style interfaces.

        Returns:
            str: The user's input, simulating the action.
        """
        # Get user input (no validation)
        action = input("Enter action: ").strip()

        return action


def run_Unity_executable(executable_path, *args):
    """
    Runs the Unity executable with optional command-line arguments and returns the process handle.

    Args:
        executable_path (str): The path to the Unity executable.
        *args: Optional command-line arguments to pass to the Unity executable.

    Returns:
        process: The subprocess.Popen process handle.
    """
    try:
        # Create the command to run the Unity executable
        command = [executable_path] + list(args)

        # Run the executable using Popen to get a process handle
        process = subprocess.Popen(command)

        print(f"Unity executable '{executable_path}' started.")

        return process  # Return the process handle so we can close it later

    except FileNotFoundError:
        print(f"The file '{executable_path}' was not found.")
        return None


def close_Unity_process(process):
    """
    Terminates the Unity executable process.

    Args:
        process: The process handle of the Unity executable.

    Returns:
        None
    """
    if process:
        process.terminate()  # This will attempt to terminate the process
        process.wait()  # Wait for the process to fully close
        print("Unity executable closed.")
    else:
        print("No process to terminate.")


def load_config_paths(config_dir):
    """
    Loads all JSON config file paths and their corresponding .png image file paths from the given directory.
    Assumes image files have the same base name as the JSON files with a .png extension.

    Args:
        config_dir (str): The path to the directory containing the JSON config and image files.

    Returns:
        tuple: A tuple of two lists:
               - List of file paths to the JSON config files.
               - List of file paths to the corresponding image files.
    """
    # Lists to store file paths
    json_file_paths = []
    image_file_paths = []

    # Iterate over all files in the directory
    for file_name in os.listdir(config_dir):
        # Check if the file has a .json extension
        if file_name.endswith(".json"):
            # Construct the full file path for the JSON file
            json_full_path = os.path.join(config_dir, file_name)
            json_file_paths.append(json_full_path)

            # Construct the corresponding image file path (assuming .png extension)
            base_name = os.path.splitext(file_name)[0]  # Remove the .json extension
            image_full_path = os.path.join(config_dir, base_name + ".png")
            image_file_paths.append(image_full_path)


    return json_file_paths, image_file_paths


def copy_json_to_unity_resources(json_config_path, unity_executable_path):
    """
    Copies a JSON config file to the Unity executable's Resources folder and renames it to puzzle.json.

    Args:
        json_config_path (str): The path to the JSON configuration file.
        unity_executable_path (str): The path to the Unity executable (e.g., 'D:/RIPPLE EXEC/RIPPLE.exe').

    Returns:
        str: The full path to the copied JSON file in the Resources folder.
    """
    # Construct the path to the Unity Resources folder
    unity_resources_folder = os.path.join(os.path.dirname(unity_executable_path), 'RIPPLE_Data', 'Resources')

    # Ensure the Resources folder exists
    if not os.path.exists(unity_resources_folder):
        raise FileNotFoundError(f"The Resources folder does not exist at: {unity_resources_folder}")

    # Define the destination path for the copied JSON file
    destination_path = os.path.join(unity_resources_folder, 'puzzle.json')

    # Copy and rename the JSON config file to the Resources folder as puzzle.json
    shutil.copy(json_config_path, destination_path)

    return destination_path


def create_experiment_directories(num_game_env, agents):
    """
    Creates a 'data/experiment_ID_{ID}/experiment_{agent_type}_{env_type}_{game_num}' subdirectory for every combination of
    agents and game environments, and for the number of games specified in num_game_env.

    Args:
        num_game_env (dict): A dictionary where keys are environment types and values are the number of games.
        agents (dict): A dictionary where keys are agent types and values are agent instances.

    Returns:
        dict: A dictionary mapping (agent_type, env_type, game_num) to the full path of each experiment directory.
    """
    # Get the current working directory (this should be inside 'source/')
    current_dir = os.getcwd()

    # Get the parent directory of 'source/' (one level up)
    parent_dir = os.path.dirname(current_dir)

    # Define the path for the 'data/' directory (one level above 'source/')
    data_dir = os.path.join(parent_dir, 'data')

    # Ensure the 'data/' directory exists (create it if it doesn't)
    os.makedirs(data_dir, exist_ok=True)

    # Generate a unique ID based on the current date and time (format: YYYYMMDD_HHMMSS)
    experiment_id = datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")

    # Create the path for the main experiment directory
    experiment_dir = os.path.join(data_dir, experiment_id)

    # Ensure the experiment directory is created
    os.makedirs(experiment_dir, exist_ok=True)

    # Dictionary to store all created subdirectory paths
    experiment_subdirs = {}

    # Loop over each agent and game environment
    for agent_type, agent in agents.items():
        if agent_type not in experiment_subdirs:
            experiment_subdirs[agent_type] = {}

        for env_type, num_games in num_game_env.items():
            if env_type not in experiment_subdirs[agent_type]:
                experiment_subdirs[agent_type][env_type] = {}

            for game_num in range(1, num_games + 1):
                # Construct the subdirectory name
                subdir_name = f"experiment_{agent_type}_{env_type}_{game_num}"

                # Create the subdirectory path inside the main experiment directory
                subdir_path = os.path.join(experiment_dir, subdir_name)

                # Ensure the subdirectory is created
                os.makedirs(subdir_path, exist_ok=True)

                # Store the path in the nested dictionary
                experiment_subdirs[agent_type][env_type][game_num] = subdir_path

    # Return the dictionary of subdirectory paths
    return experiment_subdirs


def copy_files_to_experiment(json_file_path, image_file_path, experiment_path):
    """
    Copies the JSON and image file to the specified experiment path.

    Args:
        json_file_path (str): The full path of the JSON file to be copied.
        image_file_path (str): The full path of the image file to be copied.
        experiment_path (str): The path to the experiment directory where the files should be copied.
    """
    try:
        # Ensure the experiment directory exists
        if not os.path.exists(experiment_path):
            os.makedirs(experiment_path)

        # Copy the JSON file to the experiment directory
        json_file_dest = os.path.join(experiment_path, os.path.basename(json_file_path))
        shutil.copy(json_file_path, json_file_dest)
        print(f"JSON file copied to {json_file_dest}")

        # Copy the image file to the experiment directory
        image_file_dest = os.path.join(experiment_path, os.path.basename(image_file_path))
        shutil.copy(image_file_path, image_file_dest)
        print(f"Image file copied to {image_file_dest}")

    except Exception as e:
        print(f"Error copying files: {e}")


def save_results_to_csv(experiment_path, i, win):
    """
    Saves the results (i and win) to a CSV file named 'results.csv' in the specified experiment path.

    Args:
        experiment_path (str): The path to the experiment directory where the CSV file should be saved.
        i (int): The number of actions used.
        win (bool): Whether the game was won.
    """
    # Define the path for the CSV file
    csv_file_path = os.path.join(experiment_path, 'results.csv')

    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header if the file is new
        if not file_exists:
            writer.writerow(['Game Number', 'Actions Used', 'Win'])

        # Write the result row
        writer.writerow([i, win])

    print(f"Results saved to {csv_file_path}")


if __name__ == "__main__":
    # Example usage
    Unity_executable_path = r'D:\RIPPLE EXEC\RIPPLE.exe'

    # Start the Unity executable
    process = run_Unity_executable(Unity_executable_path)

    # Wait for a while (e.g., 10 seconds) before closing it
    time.sleep(10)  # You can replace this with your actual logic to determine when to close it

    # Close the Unity executable
    close_Unity_process(process)
