import os
import glob
import json
import pandas as pd
import Source.Evaluate.evaluation_utilities as util

def compile_episode_evaluation(experiment_id, experiment_signature="InteractivePuzzle"):
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    episode_data = []

    for sub_dir in sub_dirs:
        try:
            # Use the full directory name as the episode ID
            episode_nr = os.path.basename(sub_dir)

            # Extract agent name and modality
            agent_info = episode_nr.split(f'_{experiment_signature}_')[1].split('_config_')[0]
            if '_' in agent_info:
                agent_name, modality = agent_info.split('_')
            else:
                agent_name = agent_info
                modality = 'unknown'  # Fallback if no modality is specified

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

            # Extract relevant per-episode values
            min_path_length = eval_data.get('min_path', {}).get('min_path_length', None)
            spl_value = eval_data.get('spl_value', {}).get('value', None)
            won = eval_data.get('won', False)
            won_at_spl = eval_data.get('won_at_spl', False)

            # Append episode-level data to list
            episode_data.append({
                'episode_nr': episode_nr,
                'agent': agent_name,
                'modality': modality,
                'scenario': scenario,
                'complexity_c1': complexity_c1,
                'complexity_c2': complexity_c2,
                'num_geoms': num_geoms,
                'min_path_length': min_path_length,
                'spl_value': spl_value,
                'won': won,
                'won_at_spl': won_at_spl
            })

        except Exception as e:
            print(f"Error loading file in {sub_dir}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(episode_data)
    csv_path = os.path.join(results_dir, "episode_outcomes_evaluation.csv")
    df.to_csv(csv_path, index=False)
    print(f"Episode-level data compiled and saved to {csv_path}")
    return df


if __name__ == "__main__":

    experiment_id = 'Claude_text_ICML_2'
    experiment_signature = "InteractivePuzzle"

    # Evaluate and plot for the entire experiment
    compile_episode_evaluation(experiment_id, experiment_signature=experiment_signature)