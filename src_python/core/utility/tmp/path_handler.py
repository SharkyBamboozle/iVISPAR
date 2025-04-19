
class PathHandler:
    def __init__(self):
        pass

    def get_dir(self, config_id, type='config'):
        return f"usr/{config_id}"


def load_config_paths(config_dir):
    """
    Loads all JSON config file paths and their corresponding .png image file paths (start and goal) from the given directory.
    Assumes image files have the same base name as the JSON files, with _start.png and _goal.png extensions.

    Args:
        config_dir (str): The path to the directory containing the JSON config and image files.

    Returns:
        tuple: A tuple of two lists:
               - List of file paths to the JSON config files.
               - List of dictionaries with paths to the corresponding start and goal image files.
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

            # Construct the corresponding image file paths for start and goal images
            base_name = os.path.splitext(file_name)[0]  # Remove the .json extension
            image_start_full_path = os.path.join(config_dir, base_name + "_start.png")
            image_goal_full_path = os.path.join(config_dir, base_name + "_goal.png")

            # Add the image file paths to the list, as a dictionary for start and goal
            image_file_paths.append({
                'start_image': image_start_full_path,
                'goal_image': image_goal_full_path
            })

    return json_file_paths, image_file_paths


def load_config_paths_from_ID(config_id):
    """
    Loads all JSON config file paths and their corresponding .png image file paths (start and goal) from the given directory.
    Assumes image files have the same base name as the JSON files, with _start.png and _goal.png extensions.

    Args:
        config_dir (str): The path to the directory containing the JSON config and image files.

    Returns:
        tuple: A tuple of two lists:
               - List of file paths to the JSON config files.
               - List of dictionaries with paths to the corresponding start and goal image files.
    """

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

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

            # Construct the corresponding image file paths for start and goal images
            base_name = os.path.splitext(file_name)[0]  # Remove the .json extension
            image_start_full_path = os.path.join(config_dir, base_name + "_start.png")
            image_goal_full_path = os.path.join(config_dir, base_name + "_goal.png")

            # Add the image file paths to the list, as a dictionary for start and goal
            image_file_paths.append({
                'start_image': image_start_full_path,
                'goal_image': image_goal_full_path
            })

    return json_file_paths, image_file_paths


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

    experiment_id = datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)

    # Get the current working directory (this should be inside 'source/')
    #current_dir = os.getcwd()

    # Get the parent directory of 'source/' (one level up)
    #parent_dir = os.path.dirname(current_dir)

    # Define the path for the 'data/' directory (one level above 'source/')
    #data_dir = os.path.join(parent_dir, 'data')

    # Ensure the 'data/' directory exists (create it if it doesn't)
    #os.makedirs(data_dir, exist_ok=True)

    # Generate a unique ID based on the current date and time (format: YYYYMMDD_HHMMSS)
    #experiment_id = datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")

    # Create the path for the main experiment directory
    #experiment_dir = os.path.join(data_dir, experiment_id)

    # Ensure the experiment directory is created
    #os.makedirs(experiment_dir, exist_ok=True)

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
    return experiment_subdirs, experiment_id