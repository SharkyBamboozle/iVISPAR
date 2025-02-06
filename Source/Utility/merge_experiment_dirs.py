import os
import shutil

def copy_and_episodes(experiment_id_1, experiment_id_2, add_identifier="", experiment_signature="InteractivePuzzle"):
    """
    Copies subdirectories from one experiment directory to another and appends an identifier
    to the subdirectory names after the experiment signature.

    Usecase: running multiple experiments that should be merged into one direcoty the end,
    but there are already other episodes with identical name

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


if __name__ == "__main__":
    copy_and_episodes("experiment_ID_20241219_222228_Gemini_l", "evaluate_Berkeley", add_identifier="Gemini_vision", experiment_signature="InteractivePuzzle")