import os
import glob
import json
import fnmatch
import pandas as pd
import Source.Evaluate.evaluation_utilities as util

def compile_episode_evaluation(experiment_id, experiment_signature="InteractivePuzzle"):
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

            # Attempt to load config_*.json
            config_file_path = next((os.path.join(sub_dir, f) for f in os.listdir(sub_dir) if fnmatch.fnmatch(f, "config_*.json")), None)
            if not config_file_path or not os.path.exists(config_file_path):
                print(f"No config file found in {sub_dir}. Skipping...")
                continue

            with open(config_file_path, 'r') as config_file:
                config_data = json.load(config_file)

            # Extract information from config_*.json
            complexity_c1 = config_data.get('complexity_c1', None)
            complexity_c2 = config_data.get('complexity_c2', None)
            grid_size = config_data.get('grid_size', None)
            num_geoms = max(lm['geom_nr'] for lm in config_data.get('landmarks', [])) if config_data.get('landmarks') else None

            # Load evaluation data
            eval_file_list = glob.glob(os.path.join(sub_dir, "episode_evaluation.json"))
            if not eval_file_list:
                print(f"No evaluation file found in {sub_dir}. Skipping...")
                continue

            eval_file_path = eval_file_list[0]
            with open(eval_file_path, 'r') as eval_file:
                eval_data = json.load(eval_file)

            # Extract relevant per-episode values
            min_path_length = eval_data.get('min_path', {}).get('min_path_length', None)
            spl_value = eval_data.get('spl_value', {}).get('value', None)
            won = eval_data.get('won', False)
            won_at_spl = eval_data.get('won_at_spl', False)

            # Append episode-level data to list
            episode_data.append({
                'episode_nr': episode_nr,
                'agent': agent_name,
                'model_type': model_type,
                'representation_type': representation_type,
                'config_id': config_id,
                'scenario': experiment_signature,
                'complexity_c1': complexity_c1,
                'complexity_c2': complexity_c2,
                'grid_size': grid_size,
                'num_geoms': num_geoms,
                'min_path_length': min_path_length,
                'spl_value': spl_value,
                'won': won,
                'won_at_spl': won_at_spl
            })

        except Exception as e:
            print(f"Error processing {sub_dir}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(episode_data)
    csv_path = os.path.join(results_dir, "episode_outcomes_evaluation.csv")
    df.to_csv(csv_path, index=False)
    print(f"Episode-level data compiled and saved to {csv_path}")
    return df



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    experiment_signature = "InteractivePuzzle"

    # Evaluate and plot for the entire experiment
    compile_episode_evaluation(experiment_id, experiment_signature=experiment_signature)