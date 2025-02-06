import os
import json
import pandas as pd
import Source.Evaluate.evaluation_utilities as util

def compile_mistakes(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Compile episode evaluation data from experiment directories.

    Args:
        experiment_id (str): The experiment ID to locate the experiment directory.
        experiment_signature (str): Signature to filter subdirectories (default: "InteractivePuzzle").

    Returns:
        pd.DataFrame: A DataFrame containing compiled episode data.
    """
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    episode_data = []

    for sub_dir in sub_dirs:
        try:
            # Use the full directory name as the episode ID
            episode_nr = os.path.basename(sub_dir)

            # Load evaluation data
            eval_file_list = os.path.join(sub_dir, "episode_evaluation.json")
            if not eval_file_list:
                print(f"No evaluation file found in {sub_dir}. Skipping...")
                continue

            eval_file_path = eval_file_list[0]
            with open(eval_file_path, 'r') as file:
                eval_data = json.load(file)

            # Load metadata.json
            metadata_file_path = os.path.join(sub_dir, "metadata.json")
            if not os.path.exists(metadata_file_path):
                print(f"No metadata.json file found in {sub_dir}. Skipping...")
                continue

            with open(metadata_file_path, 'r') as metadata_file:
                metadata = json.load(metadata_file)

            # Extract information from metadata.json
            agent_name = next(iter(metadata.get('agent', {}).keys()), "unknown")
            model_type = metadata.get('agent', {}).get(agent_name, {}).get('model_type', "unknown")

            game_info = metadata.get('game', {}).get(experiment_signature, {})
            representation_type = game_info.get('representation_type', "unknown")
            config_id = game_info.get('config_id', "unknown")

            # Load sim_message_log.json
            sim_message_log_file_path = os.path.join(sub_dir, "sim_message_log.json")
            if not os.path.exists(sim_message_log_file_path):
                print(f"No sim_message_log.json file found in {sub_dir}. Skipping...")
                continue

            with open(sim_message_log_file_path, 'r') as sim_message_log_file:
                sim_message_log = json.load(sim_message_log_file)

            # Count occurrences of specific strings in "valididy"
            legal_move_count = 0
            destination_occupied_count = 0
            out_of_bounds_count = 0
            not_legal_command_count = 0

            for step in sim_message_log.values():
                actions = step.get("Actions", [])
                for action in actions:
                    valididy_list = action.get("valididy", [])
                    legal_move_count += valididy_list.count("was legal move")
                    destination_occupied_count += valididy_list.count("Destination occupied")
                    out_of_bounds_count += valididy_list.count("Destination out of bounds")
                    not_legal_command_count += valididy_list.count("not a legal command")

            # Append episode-level data to list
            episode_data.append({
                'episode_nr': episode_nr,
                'agent': agent_name,
                'model_type': model_type,
                'representation_type': representation_type,
                'config_id': config_id,
                'scenario': experiment_signature,
                'legal_moves': legal_move_count,
                'destination_occupied': destination_occupied_count,
                'out_of_bounds': out_of_bounds_count,
                'not_legal_commands': not_legal_command_count
            })

        except Exception as e:
            print(f"Error processing {sub_dir}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(episode_data)
    csv_path = os.path.join(results_dir, "mistakes_evaluation.csv")
    df.to_csv(csv_path, index=False)
    print(f"Episode-level data compiled and saved to {csv_path}")
    return df



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    experiment_signature = "InteractivePuzzle"

    # Evaluate and plot for the entire experiment
    compile_mistakes(experiment_id, experiment_signature=experiment_signature)