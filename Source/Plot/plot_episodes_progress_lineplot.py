import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="darkgrid")

import Source.Evaluate.evaluation_utilities as util


def plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Plot the A* heuristic evaluations, regret, and normalized progress for each subdirectory in an experiment.
    Each subdirectory contains an 'eval_*.json' file.
    The function plots values from all these files as Seaborn line graphs, with normalized progress shown on a secondary y-axis.

    Args:
        experiment_id (str): The ID of the experiment directory.
        experiment_signature (str): Signature to filter subdirectories.
    """
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    eval_json_files_signature = "episode_evaluation.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [eval_json_files_signature, config_json_files_signature]

    for sub_dir in sub_dirs:
        print(f"Current subdir: {sub_dir}")
        list_of_sus_dirs =[
            r"C:\Users\Sharky\iVISPAR_dev\Data\Experiments\ICML_all\Episodes\episode_Claude_InteractivePuzzle_sim_param1_config_ICML_b_4_g_2_c1_6_c2_0_i_2",
            r"C:\Users\Sharky\iVISPAR_dev\Data\Experiments\ICML_all\Episodes\episode_Claude_InteractivePuzzle1_sim_param1_config_ICML_b_4_g_2_c1_8_c2_0_i_3"
        ]
        if sub_dir in list_of_sus_dirs:  # Check if sub_dir is in the list
            print("caught!")
            continue

        file_dict = util.bulk_load_files(sub_dir, file_signatures)

        try:
            # Load evaluation data
            with open(file_dict[eval_json_files_signature][0], 'r') as eval_file:
                eval_data = json.load(eval_file)

            # Load environment configuration
            with open(file_dict[config_json_files_signature][0], 'r') as config_file:
                config = json.load(config_file)

        except Exception as e:
            print(f"Error loading files for subdir {sub_dir}: {e}")
            continue

        # Extract move_heuristics, regret, and normalized progress
        move_heuristics = eval_data.get('move_heuristics').get('values')
        regret = eval_data.get('regret').get('values')
        normalized_progress = eval_data.get('normalized_progress', []).get('values')

        if not move_heuristics or not regret:
            print(f"Missing 'move_heuristics' or 'regret' in {sub_dir}, skipping.")
            continue

        # Extract complexity for optimal line plotting
        c1_complexity = config.get('complexity_c1')
        if c1_complexity is None:
            print(f"No complexity value (c1_complexity) found for {sub_dir}, skipping.")
            continue

        # Create an optimal trajectory line based on complexity
        optimal_trajectory = list(range(c1_complexity, -1, -1))

        # Padding: Ensure the length of optimal_trajectory matches the move_heuristics
        if len(optimal_trajectory) < len(move_heuristics):
            optimal_trajectory += [0] * (len(move_heuristics) - len(optimal_trajectory))

        # Plot the data
        fig, ax1 = plt.subplots(figsize=(18, 6))

        x_values = range(0, len(move_heuristics))  # x-axis represents the step numbers

        # Plot A* heuristic (agent performance over time) on the primary y-axis
        line1, = ax1.plot(x_values, move_heuristics, label="Agent Remaining Steps", color="b", linestyle='-')
        line2, = ax1.plot(x_values, optimal_trajectory, label="Optimal Steps Remaining", color="g", linestyle='--')
        line3, = ax1.plot(x_values, regret, label="Regret (Excess Moves)", color="r", linestyle=':')

        ax1.set_xlabel('Episode Step')
        ax1.set_ylabel('Remaining Steps to Reach Goal')
        ax1.set_title(f'Evaluation and Regret for {os.path.basename(sub_dir)}')

        # Create secondary y-axis for normalized progress
        ax2 = ax1.twinx()
        line4, = ax2.plot(x_values, normalized_progress, label="Normalized Progress (%)", color="orange", linestyle='-')
        ax2.set_ylabel('Progress (%)')

        # Only apply grid to the primary axis
        ax1.grid(True)
        ax2.grid(False)

        # Calculate the maximum and minimum values from the data
        min_value = min(min(regret), min(optimal_trajectory), min(move_heuristics))
        max_value = max(max(regret), max(optimal_trajectory), max(move_heuristics))

        # Define a margin (e.g., 5% of the range)
        margin = (max_value - min_value) * 0.05
        ax1_range = max_value + margin- (min(0, min_value - margin))
        scale = 100 / ax1_range

        # Set axis limits with the margin, ensuring the lower limit doesn't go above 0
        ax1.set_ylim(min(0, min_value - margin), max_value + margin)
        ax2.set_ylim(min(0, min_value - margin*scale), 100 + margin*scale)

        # Combine legends from both axes
        lines = [line1, line2, line3, line4]
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc="upper left")

        #step_size = 2  # Adjust this to control the interval (e.g., every 2 steps)
        #plt.xticks(x_values[::step_size])

        # Save the plot to the current subdirectory
        config_instance_id = config.get('config_instance_id')
        plot_path = os.path.join(sub_dir, f"steps_graph.png")
        plt.savefig(plot_path)
        plt.close()

        print(f"Plot saved at {plot_path}")



if __name__ == "__main__":

    experiment_id = 'qwen_text_test'
    experiment_signature = "InteractivePuzzle"

    plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle")
