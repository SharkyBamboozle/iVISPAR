import os
import shutil


def retrieve_config_visualisations(config_id, experiment_id):
    """
    For each subdirectory starting with 'experiment_AStarAgent', locate the JSON configuration file,
    and move the PNG and GIF files with the same `json_base_name` to the destination directory.

    Parameters:
        config_id (str): The configuration ID.
        experiment_id (str): The experiment ID.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

    # Locate all subdirectories starting with 'experiment_AStarAgent'
    target_subdirs = [os.path.join(experiment_dir, d) for d in os.listdir(experiment_dir)
                      if os.path.isdir(os.path.join(experiment_dir, d)) and d.startswith('episode_AIAgent')]
    if not target_subdirs:
        raise FileNotFoundError(
            "No subdirectories starting with 'episode_AStarAgent' found in the experiment directory.")

    # Counter for successful copies
    successful_moves = 0

    for subdir in target_subdirs:
        # Locate the JSON file in the subdirectory
        json_file = next((f for f in os.listdir(subdir) if f.startswith('config') and f.endswith('.json')), None)
        if not json_file:
            print(f"No configuration JSON file found in {subdir}. Skipping...")
            continue

        # Extract the base name of the JSON file (without the extension)
        json_base_name = os.path.splitext(json_file)[0]

        # Locate the PNG and GIF files in the same subdirectory
        png_file = next((f for f in os.listdir(subdir) if f == f"{json_base_name}.png"), None)
        mp4_file = next((f for f in os.listdir(subdir) if f == f"{json_base_name}.mp4"), None)

        # Ensure at least one of the files exists
        if not png_file and not mp4_file:
            print(f"No PNG or GIF files found for '{json_base_name}' in {subdir}. Skipping...")
            continue

        # Move the PNG file, if it exists
        if png_file:
            source_path_png = os.path.join(subdir, png_file)
            destination_path_png = os.path.join(config_dir, png_file)
            shutil.copy(source_path_png, destination_path_png)
            successful_moves += 1
            print(f"""Moved file {successful_moves} (PNG):
                - - - from: {source_path_png}
                - - - to: {destination_path_png}

            """)

        # Move the MP4 file, if it exists
        if mp4_file:
            source_path_mp4 = os.path.join(subdir, mp4_file)
            destination_path_mp4 = os.path.join(config_dir, mp4_file)
            shutil.copy(source_path_mp4, destination_path_mp4)
            successful_moves += 1
            print(f"""Moved file {successful_moves} (MP4):
                - - - from: {source_path_mp4}
                - - - to: {destination_path_mp4}

            """)

    print(f"Total files moved: {successful_moves}")


if __name__ == "__main__":
    config_id = "SGP_ID_Berkeley_submission"
    experiment_id = "experiment_ID_20241219_152121"

    retrieve_config_visualisations(config_id, experiment_id)