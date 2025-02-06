"""
Utility function: add specific model to meta data for one use case
"""

import evaluation_utilities as util
import os
import json

def add_to_metadata(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Add or update the model_type field in metadata.json files for all subdirectories in the experiment.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle").
    """
    # Get directory and file paths
    experiment_dir, _ = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Model type to add
    model_type = "claude-3-5-sonnet-20241022"

    for sub_dir in sub_dirs:
        metadata_path = os.path.join(sub_dir, "metadata.json")

        if os.path.exists(metadata_path):
            try:
                # Load the metadata file
                with open(metadata_path, "r") as file:
                    metadata = json.load(file)

                # Add or update the `model_type` field
                if 'agent' in metadata and isinstance(metadata['agent'], dict):
                    for agent_name, agent_info in metadata['agent'].items():
                        if 'agent_type' in agent_info:
                            metadata['agent'][agent_name]['model_type'] = model_type

                # Save the updated metadata back to the file
                with open(metadata_path, "w") as file:
                    json.dump(metadata, file, indent=4)

                print(f"Updated metadata in {metadata_path}")

            except Exception as e:
                print(f"Error updating {metadata_path}: {e}")
        else:
            print(f"No metadata.json found in {sub_dir}, skipping...")

def correct_game_key_in_metadata(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Correct the game key in metadata.json files by renaming 'InteractivePuzzle1' to 'InteractivePuzzle'.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle").
    """
    # Get directory and file paths
    experiment_dir, _ = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    for sub_dir in sub_dirs:
        metadata_path = os.path.join(sub_dir, "metadata.json")

        if os.path.exists(metadata_path):
            try:
                # Load the metadata file
                with open(metadata_path, "r") as file:
                    metadata = json.load(file)

                # Check and correct the game key
                if 'game' in metadata and isinstance(metadata['game'], dict):
                    if "InteractivePuzzle1" in metadata['game']:
                        metadata['game']["InteractivePuzzle"] = metadata['game'].pop("InteractivePuzzle1")

                # Save the updated metadata back to the file
                with open(metadata_path, "w") as file:
                    json.dump(metadata, file, indent=4)

                print(f"Corrected game key in {metadata_path}")

            except Exception as e:
                print(f"Error updating {metadata_path}: {e}")
        else:
            print(f"No metadata.json found in {sub_dir}, skipping...")

def update_model_type_in_metadata(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Update the model_type value in metadata.json files for all subdirectories in the experiment.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle").
    """
    # Get directory and file paths
    experiment_dir, _ = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    for sub_dir in sub_dirs:
        metadata_path = os.path.join(sub_dir, "metadata.json")

        if os.path.exists(metadata_path):
            try:
                # Load the metadata file
                with open(metadata_path, "r") as file:
                    metadata = json.load(file)

                # Update the model_type in the agent section
                if 'agent' in metadata and isinstance(metadata['agent'], dict):
                    for agent_name, agent_info in metadata['agent'].items():
                        if 'model_type' in agent_info:
                            old_model_type = agent_info['model_type']
                            new_model_type = f"{old_model_type}-bug"  # Append '-bug' to the existing model_type
                            metadata['agent'][agent_name]['model_type'] = new_model_type

                # Save the updated metadata back to the file
                with open(metadata_path, "w") as file:
                    json.dump(metadata, file, indent=4)

                print(f"Updated model_type in {metadata_path}")

            except Exception as e:
                print(f"Error updating {metadata_path}: {e}")
        else:
            print(f"No metadata.json found in {sub_dir}, skipping...")


if __name__ == "__main__":
    #experiment_id = 'Claude_text_ICML_1'
    #add_to_metadata(experiment_id)


    experiment_id = "ICML_all"
    update_model_type_in_metadata(experiment_id)