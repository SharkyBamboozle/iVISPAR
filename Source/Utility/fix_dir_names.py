"""
Utility function: Rename subdirectories in the experiment directory by replacing old characters with new ones.
"""

import os
import evaluation_utilities as util


def fix_dir_names(experiment_id, old_chars, new_chars, experiment_signature="InteractivePuzzle"):
    """
    Rename subdirectories in the experiment directory by replacing old characters with new ones.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        old_chars (str): The characters to be replaced in directory names.
        new_chars (str): The characters to replace with.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle").
    """
    # Get directory and file paths
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Loop over directories
    for sub_dir in sub_dirs:
        # Extract the directory name
        dir_name = os.path.basename(sub_dir)
        new_dir_name = dir_name.replace(old_chars, new_chars)

        # Rename the directory if the name has changed
        if new_dir_name != dir_name:
            old_path = os.path.join(experiment_dir, "Episodes", dir_name)
            new_path = os.path.join(experiment_dir, "Episodes", new_dir_name)

            try:
                os.rename(old_path, new_path)
                print(f"Renamed: {dir_name} -> {new_dir_name}")
            except Exception as e:
                print(f"Error renaming {dir_name}: {e}")

    print("Directory renaming completed.")


if __name__ == "__main__":
    experiment_id = 'Qwen_vision_3D'

    old_chars = "sim_param1"
    new_chars = "vision3D"
    fix_dir_names(experiment_id, old_chars, new_chars)
