import json
import os

def expand_config_file(experiment_path, grid_label, camera_offset, camera_auto_override, screenshot_alpha):
    """
    Traverse a dictionary containing nested paths or process a single directory path,
    locate JSON files, update them with additional values, and save the updated JSONs back to the same files.

    Parameters:
        experiment_dic (dict or str): A nested dictionary of paths or a single directory path.
        grid_label (str): One of ['edge', 'cell', 'both', 'none'] to add to the JSON.
        camera_offset (list): A list of three numbers [x, y, z] to add to the JSON.
        screenshot_alpha (float): A float value to add to the JSON.
    """

    #TODO mkdir new config with name_extended
    #TODO Copy configs from there to new dir

    # Check for valid grid_label
    valid_grid_labels = {'edge', 'cell', 'both', 'none'}
    if grid_label not in valid_grid_labels:
        raise ValueError(f"Invalid grid_label '{grid_label}'. Must be one of {valid_grid_labels}.")

    # If a single path string is passed, wrap it into a dictionary-like structure
    if isinstance(experiment_path, str):
        experiment_dic = {"single_path": {"sub_path": {1: experiment_path}}}

    # Traverse the nested dictionary and process each directory
    for agent, environments in experiment_dic.items():
        for env_type, games in environments.items():
            for game_num, directory_path in games.items():

                if not os.path.isdir(directory_path):
                    print(f"Skipping invalid directory: {directory_path}")
                    continue

                # Locate JSON files in the directory
                json_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith('.json')]

                if not json_files:
                    print(f"No JSON files found in directory: {directory_path}")
                    continue

                for json_file in json_files:
                    try:
                        # Load the JSON config
                        with open(json_file, 'r') as file:
                            config = json.load(file)

                        # Add the new values
                        config["grid_label"] = grid_label
                        config["camera_offset"] = camera_offset
                        config['camera_auto_override'] = camera_auto_override
                        config["screenshot_alpha"] = screenshot_alpha

                        # Save the updated JSON back to the file
                        with open(json_file, 'w') as file:
                            json.dump(config, file, indent=4)

                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Error processing file {json_file}: {e}")

    return config



if __name__ == "__main__":
    # Parameters
    # Simulation parameter

    config_id = 'SGP_ID_20241206_225133_x'

    sim_param = {
        'grid_label': 'both', #choices are between 'edge', 'cell' , 'both' and 'none'
        'camera_offset': [0,5.57,-3.68],
        'camera_auto_override': [6.8,-1,6.8],
        'screenshot_alpha': 0.0,
    }


    expand_config_file(
        experiment_path=config_id,
        grid_label=sim_param.get('grid_label', None),
        camera_offset=sim_param.get('camera_offset', None),
        camera_auto_override=sim_param.get('camera_auto_override', None),
        screenshot_alpha=sim_param.get('screenshot_alpha', None)
    )