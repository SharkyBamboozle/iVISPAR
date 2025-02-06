import os
import shutil
import subprocess
import time
import csv
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import fnmatch


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
        return params
    except Exception as e:
        return {}


def load_single_json_from_directory(directory_path):
    """
    Finds and loads a single JSON file from the specified directory.

    Parameters:
        directory_path (str): Path to the directory containing the JSON file.

    Returns:
        dict: Parsed JSON content as a dictionary.

    Raises:
        FileNotFoundError: If no JSON files are found in the directory.
        ValueError: If more than one JSON file is found in the directory.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"The directory does not exist: {directory_path}")

    # Find all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if fnmatch.fnmatch(f, 'config*.json')]

    if len(json_files) == 0:
        raise FileNotFoundError(f"No JSON files found in the directory: {directory_path}")
    if len(json_files) > 1:
        raise ValueError(f"Multiple JSON files found in the directory: {json_files}. Specify the exact file.")

    # Load the single JSON file
    file_path = os.path.join(directory_path, json_files[0])
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error decoding JSON file: {file_path}. Details: {str(e)}")


def expand_config_file(experiment_path, grid_label, camera_offset, camera_auto_override, screenshot_alpha, auto_done_check=True):
    """
    Traverse a dictionary containing nested paths or process a single directory path,
    locate JSON files, update them with additional values, and save the updated JSONs back to the same files.

    Parameters:
        experiment_dic (dict or str): A nested dictionary of paths or a single directory path.
        grid_label (str): One of ['edge', 'cell', 'both', 'none'] to add to the JSON.
        camera_offset (list): A list of three numbers [x, y, z] to add to the JSON.
        screenshot_alpha (float): A float value to add to the JSON.
    """
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
                json_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if
                              fnmatch.fnmatch(f, 'config*.json')]

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
                        config["auto_done_check"] = auto_done_check


                        # Save the updated JSON back to the file
                        with open(json_file, 'w') as file:
                            json.dump(config, file, indent=4)

                    except (json.JSONDecodeError, IOError) as e:
                        print(f"Error processing file {json_file}: {e}")

    return config



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


def copy_files_to_experiment(json_file_path, image_file_paths, experiment_path):
    """
    Copies the JSON and image files (start and goal) to the specified experiment path.

    Args:
        json_file_path (str): The full path of the JSON file to be copied.
        image_file_paths (dict): A dictionary containing the full paths of the start and goal image files to be copied.
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

        # Copy the start and goal image files to the experiment directory
        for key, image_file_path in image_file_paths.items():
            image_file_dest = os.path.join(experiment_path, os.path.basename(image_file_path))
            shutil.copy(image_file_path, image_file_dest)
            print(f"{key.replace('_', ' ').capitalize()} copied to {image_file_dest}")

    except Exception as e:
        print(f"Error copying files: {e}")



def copy_json_to_experiment(json_file_path, experiment_path):
    """
    Copies the JSON and PNG files (with the same base name) to the specified experiment path.

    Args:
        json_file_path (str): The full path of the JSON file to be copied.
        experiment_path (str): The path to the experiment directory where the files should be copied.
    """
    try:
        # Ensure the experiment directory exists
        if not os.path.exists(experiment_path):
            os.makedirs(experiment_path)

        # Copy the JSON file to the experiment directory
        json_file_dest = os.path.join(experiment_path, os.path.basename(json_file_path))
        shutil.copy(json_file_path, json_file_dest)

        # Copy the PNG file with the same name as the JSON file
        png_file_path = os.path.splitext(json_file_path)[0] + '.png'  # Replace .json with .png
        if os.path.exists(png_file_path):
            png_file_dest = os.path.join(experiment_path, os.path.basename(png_file_path))
            shutil.copy(png_file_path, png_file_dest)

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


def merge_images(single_img_filename, obs_dir, bar_width=20, bar_height=80, text_fraction=0.3):
    """
    Merges two images side by side with a white bar in between, and adds a white bar underneath
    with centered text indicating "Current State" and "Goal State", dynamically adjusting font size.

    Args:
        single_img_filename (str): Path to the first image file.
        obs_dir (str): Directory containing the second image file named "obs_1_init.png".
        bar_width (int): Width of the white bar between the images.
        bar_height (int): Height of the white bar below the images for text labels.
        text_fraction (float): Portion of image width for the text size (0 < text_fraction <= 1).
    """
    # Path to the second image (always named obs_1_init in obs_dir)
    second_image_path = os.path.join(obs_dir, "obs_1_init.png")

    # Load the two images
    img1 = Image.open(single_img_filename)
    img2 = Image.open(second_image_path)

    # Ensure both images have the same height
    if img1.height != img2.height:
        raise ValueError("Both images should have the same height for merging.")

    # Create a new image with width = sum of both image widths + the white bar width
    total_width = img1.width + img2.width + bar_width
    total_height = img1.height + bar_height  # Additional space at the bottom for text labels
    result = Image.new('RGB', (total_width, total_height), (255, 255, 255))  # White background

    # Paste the two images onto the result image
    result.paste(img1, (0, 0))  # Paste the first image on the left
    result.paste(img2, (img1.width + bar_width, 0))  # Paste the second image on the right

    # Draw the text labels on the white bar below the images
    draw = ImageDraw.Draw(result)

    # Text labels
    text_current = "Current State"
    text_goal = "Goal State"

    # Dynamically adjust font size based on image width and text_fraction
    fontsize = 1  # Start with font size 1
    font_path = "arial.ttf"  # Use a default or available TTF font path on your system
    font = ImageFont.truetype(font_path, fontsize)

    # Increase font size until it fits the desired fraction of image width
    while draw.textbbox((0, 0), text_current, font=font)[2] < text_fraction * img1.width:
        fontsize += 1
        font = ImageFont.truetype(font_path, fontsize)

    # Optionally decrease by 1 to ensure it's less than or equal to the desired fraction
    fontsize -= 1
    font = ImageFont.truetype(font_path, fontsize)

    # Calculate text width and position based on the new font size
    current_text_width = draw.textbbox((0, 0), text_current, font=font)[2]  # Use textbbox
    goal_text_width = draw.textbbox((0, 0), text_goal, font=font)[2]  # Use textbbox

    # Calculate text positions to center them below each image
    current_text_x = (img1.width - current_text_width) // 2
    goal_text_x = img1.width + bar_width + (img2.width - goal_text_width) // 2

    text_y = img1.height + (bar_height // 4)  # Adjust text height to be centered in the bar

    # Draw the text labels
    draw.text((current_text_x, text_y), text_current, fill="black", font=font)
    draw.text((goal_text_x, text_y), text_goal, fill="black", font=font)

    # Split the filename and extension
    file_root, file_ext = os.path.splitext(single_img_filename)
    double_img_file_name = f"{file_root}_compare{file_ext}"

    # Save the result back to the output directory with the modified name
    output_path = os.path.join(obs_dir, os.path.basename(double_img_file_name))
    result.save(output_path)

    print(f"Merged image saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    Unity_executable_path = r'D:\RIPPLE EXEC\RIPPLE.exe'

    # Start the Unity executable
    process = run_Unity_executable(Unity_executable_path)

    # Wait for a while (e.g., 10 seconds) before closing it
    time.sleep(10)  # You can replace this with your actual logic to determine when to close it

    # Close the Unity executable
    close_Unity_process(process)

    # Example usage:
    directory_path = "/path/to/your/json_directory"
    try:
        json_data = load_single_json_from_directory(directory_path)
        print("JSON data loaded successfully:", json_data)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(e)