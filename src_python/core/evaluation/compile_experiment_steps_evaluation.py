"""
- This code compiles the evaluation from individual episodes into csv files for the different statistics
- The csv file gets saved into the results dir with the same ID name as the experiment
- From this csv file the evaluation can be plotted
"""
import os
import json
import pandas as pd
import glob
import Source.Evaluate.evaluation_utilities as util


def compile_experiment_evaluation(experiment_id, experiment_signature="InteractivePuzzle"):
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    episode_data = []

    max_steps = 20  # Define the maximum steps for all episodes

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

            scenario = experiment_signature
            complexity_c1 = int(episode_nr.split('_c1_')[1].split('_')[0])
            complexity_c2 = int(episode_nr.split('_c2_')[1].split('_')[0])
            num_geoms = int(episode_nr.split('_g_')[1].split('_')[0])

            # Load evaluation data
            eval_file_list = glob.glob(os.path.join(sub_dir, "episode_evaluation.json"))
            if not eval_file_list:
                print(f"No evaluation file found in {sub_dir}. Skipping...")
                continue

            eval_file_path = eval_file_list[0]
            with open(eval_file_path, 'r') as file:
                eval_data = json.load(file)

            # Ensure data exists for all metrics
            move_heuristics = eval_data.get('move_heuristics', {}).get('values', [])
            regret = eval_data.get('regret', {}).get('values', [])
            normalized_progress = eval_data.get('normalized_progress', {}).get('values', [])

            # Determine the actual length of the episode
            episode_length = len(move_heuristics)

            # Apply padding or truncation based on max_steps
            if episode_length < max_steps:
                # PADDING: Extend each list to max_steps
                move_heuristics += [0] * (max_steps - episode_length)
                last_regret = regret[-1] if regret else 0
                regret += [last_regret] * (max_steps - episode_length)
                normalized_progress += [100] * (max_steps - episode_length)
            else:
                # TRUNCATION: Slice the lists to max_steps
                move_heuristics = move_heuristics[:max_steps]
                regret = regret[:max_steps]
                normalized_progress = normalized_progress[:max_steps]

            # Append to DataFrame with all metrics in the same row
            for step_idx in range(max_steps):
                episode_data.append({
                    'episode_nr': episode_nr,
                    'episode_step': step_idx,
                    'agent': agent_name,
                    'config_id': config_id,
                    'model_type': model_type,
                    'representation_type': representation_type,
                    'scenario': scenario,
                    'complexity_c1': complexity_c1,
                    'complexity_c2': complexity_c2,
                    'num_geoms': num_geoms,
                    'move_heuristics': move_heuristics[step_idx],
                    'regret': regret[step_idx],
                    'normalized_progress': normalized_progress[step_idx],
                    'valid': eval_data.get('move_heuristics', {}).get('valid', False),
                    'error': eval_data.get('move_heuristics', {}).get('error', None)
                })
        except Exception as e:
            print(f"Error loading file in {sub_dir}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(episode_data)
    csv_path = os.path.join(results_dir, "episode_steps_evaluation.csv")
    df.to_csv(csv_path, index=False)
    print(f"Data compiled and saved to {csv_path}")
    return df



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    experiment_signature = "InteractivePuzzle"

    # Evaluate and plot for the entire experiment
    compile_experiment_evaluation(experiment_id, experiment_signature=experiment_signature)