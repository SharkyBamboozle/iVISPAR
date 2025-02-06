"""
Utility function: copy the ICML ds chunks from experiments into individual folder to make seperat plots
"""

import shutil
import os
import evaluation_utilities as util

def copy_ICML_chunks_into_i_123(experiment_id, experiment_signature="InteractivePuzzle1"):
    """
    Copy subdirectories matching a specific pattern into target directories based on their i value.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle1").
    """
    # Get directory and file paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    target_dir = os.path.join(base_dir, 'Data', 'Experiments')
    experiment_dir, _ = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Create directories for i_1, i_2, and i_3
    target_dirs = {}
    for i in range(1, 4):
        i_dir = os.path.join(target_dir, f"{experiment_id}_i_{i}", "Episodes")
        os.makedirs(i_dir, exist_ok=True)
        target_dirs[f"i_{i}"] = i_dir

    # Copy subdirectories based on the i value
    for sub_dir in sub_dirs:
        base_name = os.path.basename(sub_dir)
        if base_name.endswith("_i_1"):
            shutil.copytree(sub_dir, os.path.join(target_dirs["i_1"], base_name), dirs_exist_ok=True)
        elif base_name.endswith("_i_2"):
            shutil.copytree(sub_dir, os.path.join(target_dirs["i_2"], base_name), dirs_exist_ok=True)
        elif base_name.endswith("_i_3"):
            shutil.copytree(sub_dir, os.path.join(target_dirs["i_3"], base_name), dirs_exist_ok=True)

    print("Subdirectories copied successfully.")

if __name__ == "__main__":
    experiment_id = "Claude_vision_ICML"
    copy_ICML_chunks_into_i_123(experiment_id)
