import os
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set_theme(style="darkgrid")


from evaluation_utilities import make_results_dir, filter_experiment_sub_dirs, bulk_load_files
from evaluation_utilities import extract_all_states_from_config, compile_episode_data_to_data_frame
from find_shortest_move_sequence import a_star


def evaluate_episodes_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle"):
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
    Compile A* heuristic data from multiple subdirectories into a 3D DataFrame-like structure.
    Each unique agent type will be treated as a separate dimension in the DataFrame,
    and each episode's raw heuristic data will be kept without averaging.

    Args:
        experiment_id (str): The experiment identifier.
        experiment_signature (str): Part of the subdirectory name used to identify relevant episodes.

    Returns:
        pd.DataFrame: A 3D-like DataFrame with MultiIndex (episode_nr, episode_step) and agent columns.
    """
    # Directories
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Identify the unique agent names from the subdirectory names
    agent_names = set()
    for sub_dir in sub_dirs:
        folder_name = os.path.basename(sub_dir)
        # Remove 'episode_' prefix and extract agent name
        agent_name = folder_name.replace('episode_', '', 1).split(f'_{experiment_signature}')[0]
        agent_names.add(agent_name)

    # Store data for each agent in a dictionary
    agent_data = {agent: [] for agent in agent_names}

    for agent_name in agent_names:
        print(f"Processing agent: {agent_name}")

        # Filter subdirectories corresponding to this specific agent
        agent_sub_dirs = [
            sub_dir for sub_dir in sub_dirs
            if os.path.basename(sub_dir).replace('episode_', '', 1).startswith(agent_name)
        ]

        for episode_nr, sub_dir in enumerate(agent_sub_dirs):
            try:
                # Load the episode data (list of heuristic values) from the file
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

            # Store the heuristic data for this episode
            for step_idx, heuristic_value in enumerate(move_heuristics):
                agent_data[agent_name].append({
                    'episode_nr': episode_nr,
                    'episode_step': step_idx,
                    'value': heuristic_value
                })

    # Convert agent_data into a DataFrame for each agent
    data_frames = []
    for agent_name, data in agent_data.items():
        df = pd.DataFrame(data)
        df['agent'] = agent_name  # Add agent identifier
        data_frames.append(df)

    # Concatenate all DataFrames for each agent
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Pivot the DataFrame to create a MultiIndex structure
    combined_df = combined_df.pivot(index=['episode_nr', 'episode_step'], columns='agent', values='value')

    # Save the combined DataFrame as a CSV file
    csv_filename = "a_star_heuristic.csv"
    csv_path = os.path.join(results_dir, csv_filename)
    combined_df.to_csv(csv_path)
    print(f"Data compiled and saved to {csv_path}")

    return combined_df


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
    plot_csv_with_confidence_interval(experiment_id, 'a_star_heuristic.csv')
    #plot_experiment_evaluate_a_star_heuristic(experiment_id, experiment_signature=experiment_signature,c1_complexity=16)


def plot_csv_with_confidence_interval(experiment_id, csv_file_name):
    """
    Reads a 3D CSV file, processes the data, and plots multiple line graphs
    with error bands (confidence interval) for each agent.

    Args:
        experiment_id (str): The experiment ID to locate the results directory.
        csv_file_name (str): The name of the CSV file to be read.
    """
    # Load the CSV file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    csv_path = os.path.join(results_dir, csv_file_name)
    df = pd.read_csv(csv_path, header=0)

    # Exclude non-agent columns
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Set the Seaborn style
    sns.set_style('darkgrid')

    # Create the plot
    plt.figure(figsize=(18, 6))

    # Loop through each agent and plot its mean and standard deviation as an error band
    for agent in agent_columns:
        # Group by 'episode_step' and calculate mean and std
        grouped_df = df.groupby('episode_step')[agent]

        means = grouped_df.mean()
        std_devs = grouped_df.std()

        # Create the x-axis values (0, 1, 2, ..., n)
        x_values = means.index

        # Plot the mean line for this agent
        plt.plot(x_values, means, label=f"{agent}", linestyle='-', linewidth=2)

        # Plot the shaded area as the error band (mean ± std)
        plt.fill_between(x_values, means - std_devs, means + std_devs, alpha=0.2)

    # Invert the y-axis so the highest value is at the bottom and 0 at the top
    plt.gca().invert_yaxis()

    # Set axis labels and title
    plt.xlabel('Step')
    plt.ylabel('Distance to Goal')
    plt.title('LVLM evaluation on the SGP')

    # Add sub-caption below the plot
    plt.figtext(0.5, -0.05, 'This is a sub-caption below the plot', ha='center', va='center', fontsize=10, style='italic')

    # Add legend
    plt.legend(loc="upper right")

    # Save the plot to the results directory
    plot_path = os.path.join(results_dir, f"a_star_heuristic_evaluation.png")
    plt.savefig(plot_path)
    plt.show()


if __name__ == "__main__":

    experiment_id = 'experiment_SGP_c1_16'
    evaluate_a_star_heuristic(experiment_id)