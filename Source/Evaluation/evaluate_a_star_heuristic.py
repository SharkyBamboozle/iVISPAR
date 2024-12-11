import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from evaluation_utilities import make_results_dir, filter_experiment_sub_dirs, bulk_load_files, extract_all_states_from_config
from find_shortest_move_sequence import a_star


def  evaluate_episodes_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):
    # Set signatures and file paths
    system_json_files_signature = "sim_message_log.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [system_json_files_signature, config_json_files_signature]

    # Get directory and file paths
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Loop over directories
    for sub_dir in sub_dirs:
        file_dict = bulk_load_files(sub_dir, file_signatures)
        # Load board size, goal state and current step state
        try:
            with open(file_dict[system_json_files_signature][0], 'r') as system_config_file:
                system_config = json.load(system_config_file)
            with open(file_dict[config_json_files_signature][0], 'r') as env_config_file:
                env_config = json.load(env_config_file)
        except Exception as e:
            print(f"Error loading file")

        # Get states and board size
        board_size = env_config.get('grid_size')
        move_heuristics = []
        step_states = extract_all_states_from_config(system_config)
        goal_state = step_states.pop(0)

        # Loop over each step
        for step_state in step_states:
            shortest_move_sequence = a_star(board_size, step_state, goal_state)
            shortest_move_sequence_length =  len(shortest_move_sequence) -1
            move_heuristics.append(shortest_move_sequence_length)

        # Save the board state as a JSON file
        try:
            episode_A_star_eval_json_file_path = os.path.join(sub_dir, "episode_A_star_eval.json")
            with open(episode_A_star_eval_json_file_path, 'w') as f:
                json.dump(move_heuristics, f, indent=4)
        except Exception as e:
            print(f"Error saving board state to {episode_A_star_eval_json_file_path}.json: {e}")



def evaluate_experiment_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Evaluate the A* heuristic for an entire experiment, collecting and averaging the move heuristics
    at each step from multiple subdirectories.

    Args:
        experiment_id (str): The unique ID for the experiment.
        experiment_signature (str): The signature to identify relevant subdirectories for this experiment.
    """
    # Directories
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # To hold all move heuristic values for each step (list of lists)
    step_heuristics = []

    # Loop over directories
    for sub_dir in sub_dirs:
        try:
            file_path = os.path.join(sub_dir, "episode_A_star_eval.json")
            with open(file_path, 'r') as file:
                move_heuristics = json.load(file)
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            continue  # Skip this subdirectory if there is an error

        # Check if move_heuristics is valid
        if not isinstance(move_heuristics, list):
            print(f"Invalid data in {file_path}: not a list")
            continue

        # Add move heuristic values to the step_heuristics array
        for i, value in enumerate(move_heuristics):
            if len(step_heuristics) <= i:  # If the current step does not exist, expand the list
                step_heuristics.append([])
            step_heuristics[i].append(value)  # Add the value for this step

    # Calculate the average for each step
    experiment_move_heuristic = [np.mean(step) if len(step) > 0 else 0 for step in step_heuristics]

    # Save the average move heuristic for each step as a JSON file
    episode_A_star_eval_filename = "experiment_A_star_eval.json"
    episode_A_star_eval_filename_path = os.path.join(results_dir, episode_A_star_eval_filename)
    try:
        with open(episode_A_star_eval_filename_path, 'w') as f:
            json.dump(experiment_move_heuristic, f, indent=4)  # Save the average move heuristic per step
    except Exception as e:
        print(f"Error saving board state to {episode_A_star_eval_filename_path}: {e}")


def plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Plot the A* heuristic evaluations for each subdirectory in an experiment.
    Each subdirectory contains an 'episode_A_star_eval.json' file.
    The function will plot the values from all these files as a Seaborn line graph.

    Args:
        experiment_id (str): The ID of the experiment directory.
    """
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    system_json_files_signature = "episode_A_star_eval.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [system_json_files_signature, config_json_files_signature]

    for sub_dir in sub_dirs:
        file_dict = bulk_load_files(sub_dir, file_signatures)

        try:
            with open(file_dict[system_json_files_signature][0], 'r') as system_config_file:
                a_star_eval = json.load(system_config_file)
            with open(file_dict[config_json_files_signature][0], 'r') as env_config_file:
                env_config = json.load(env_config_file)
        except Exception as e:
            print(f"Error loading file for subdir {sub_dir}: {e}")
            continue

        c1_complexity = env_config.get('complexity_c1')
        if c1_complexity is None:
            print(f"No complexity value (c1_complexity) found for {sub_dir}, skipping.")
            continue

        if not a_star_eval:
            print(f"No evaluation data in {sub_dir}, skipping.")
            continue

        # Calculate optimal trajectory
        optimal_trajectory = [max(0, c1_complexity - i) for i in range(len(a_star_eval))]

        # Calculate regret (how far behind the agent is relative to optimal)
        regret = [agent_value - optimal_value for agent_value, optimal_value in zip(a_star_eval, optimal_trajectory)]

        # Plot the data
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))

        x_values = range(1, len(a_star_eval) + 1)  # x-axis represents the step numbers

        # Plot A* heuristic
        plt.plot(x_values, a_star_eval, label="Agent Remaining Steps", color="b", linestyle='--')

        # Plot Optimal Trajectory
        plt.plot(x_values, optimal_trajectory, label="Optimal Steps Remaining", color="g", linestyle='-')

        # Plot Regret
        plt.plot(x_values, regret, label="Regret (Excess Moves)", color="r", linestyle=':')

        plt.xlabel('Step')
        plt.ylabel('Number of Remaining Steps')
        plt.title(f'A* Heuristic Evaluation and Regret for Subdir {os.path.basename(sub_dir)}')
        plt.legend(loc="upper right")

        # Save the plot to the current subdirectory
        plot_path = os.path.join(sub_dir, f"a_star_heuristic_evaluation.png")
        plt.savefig(plot_path)
        plt.close()  # Close the figure to prevent memory issues

        print(f"Plot saved at {plot_path}")



def plot_experiment_evaluate_a_star_heuristic(experiment_id, c1_complexity, experiment_signature="InteractivePuzzle"):
    """
    Plot the A* heuristic evaluations for the average path from the experiment results.
    The function will plot the Agent Remaining Steps, Optimal Steps Remaining, and Regret (Excess Moves)
    using the 'experiment_A_star_eval.json' file in the results directory.

    Args:
        experiment_id (str): The ID of the experiment directory.
        c1_complexity (int): The optimal number of steps required to solve the problem.
        experiment_signature (str): The signature to filter specific experiments (default is "InteractivePuzzle").
    """
    # Directories
    experiment_dir, results_dir = make_results_dir(experiment_id)

    # Path to the evaluation file
    eval_file_path = os.path.join(results_dir, "experiment_A_star_eval.json")

    # Check if the file exists
    if not os.path.isfile(eval_file_path):
        print(f"Evaluation file not found at {eval_file_path}. Exiting function.")
        return

    # Load the evaluation data
    try:
        with open(eval_file_path, 'r') as file:
            a_star_eval = json.load(file)
    except Exception as e:
        print(f"Error loading file {eval_file_path}: {e}")
        return

    if not a_star_eval:
        print(f"No evaluation data in {eval_file_path}, exiting.")
        return

    # Calculate the optimal trajectory for each step
    optimal_trajectory = [max(0, c1_complexity - i) for i in range(len(a_star_eval))]

    # Calculate regret (how far behind the agent is relative to optimal)
    regret = [agent_value - optimal_value for agent_value, optimal_value in zip(a_star_eval, optimal_trajectory)]

    # Plot the data
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(15, 5))

    x_values = range(1, len(a_star_eval) + 1)  # x-axis represents the step numbers

    # Plot A* heuristic
    plt.plot(x_values, a_star_eval, label="Agent Remaining Steps", color="b", linestyle='--')

    # Plot Optimal Trajectory
    plt.plot(x_values, optimal_trajectory, label="Optimal Steps Remaining", color="g", linestyle='-')

    # Plot Regret
    plt.plot(x_values, regret, label="Regret (Excess Moves)", color="r", linestyle=':')

    plt.xlabel('Step')
    plt.ylabel('Number of Remaining Steps')
    plt.title(f'A* Heuristic Evaluation and Regret for Experiment {experiment_id}')
    plt.legend(loc="upper right")

    # Save the plot to the results directory
    plot_path = os.path.join(results_dir, f"a_star_heuristic_evaluation.png")
    plt.savefig(plot_path)
    plt.close()  # Close the figure to prevent memory issues

    print(f"Plot saved at {plot_path}")



def evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):

    # Evaluate and plot for each episode of the experiment
    evaluate_episodes_a_star_heuristic(experiment_id, experiment_signature=experiment_signature)
    plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature=experiment_signature)

    # Evaluate and plot for the entire experiment
    evaluate_experiment_a_star_heuristic(experiment_id, experiment_signature=experiment_signature)
    plot_experiment_evaluate_a_star_heuristic(experiment_id, experiment_signature=experiment_signature, c1_complexity=16)


if __name__ == "__main__":

    #experiment_id = 'experiment_ID_20241210_105706'
    #experiment_id = "experiment_ID_20241210_143209"
    #experiment_id = 'experiment_ID_20241210_190506'

    #Rand ds
    #experiment_id = 'experiment_ID_20241210_221901'
    #Rand 2nd attempt
    experiment_id = 'experiment_ID_20241210_223616'

    evaluate_a_star_heuristic(experiment_id)