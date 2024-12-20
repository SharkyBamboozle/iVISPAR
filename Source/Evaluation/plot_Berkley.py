import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json

from evaluation_utilities import make_results_dir, filter_experiment_sub_dirs, bulk_load_files
from evaluation_utilities import clean_and_process_normalized_progress, clean_and_process_pd_frame


def reduce_episode_data(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Extracts 'regret' values from each subdirectory in the experiment.
    The 'regret' is determined by using the 'complexity_c1' as an index
    to get the corresponding value from the eval_config.

    Args:
        experiment_id (str): The experiment identifier.
        experiment_signature (str): Signature to filter relevant directories.
    """
    # Set signatures and file paths
    eval_json_files_signature = "episode_A_star_eval.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [eval_json_files_signature, config_json_files_signature]

    # Get directory and file paths
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)
    print(f"Number of subdirectories: {len(sub_dirs)}")

    for sub_dir in sub_dirs:
        try:
            # Load files matching the signatures in the subdirectory
            file_dict = bulk_load_files(sub_dir, file_signatures)

            # Load eval config
            eval_config_path = file_dict[eval_json_files_signature][0]
            with open(eval_config_path, 'r') as eval_config_file:
                eval_config = json.load(eval_config_file)

            # Load env config
            env_config_path = file_dict[config_json_files_signature][0]
            with open(env_config_path, 'r') as env_config_file:
                env_config = json.load(env_config_file)

            # Extract 'complexity_c1' from env_config
            complexity_c1 = env_config.get('complexity_c1')
            if complexity_c1 is None:
                print(f"Warning: 'complexity_c1' not found in {env_config_path}")
                continue

            # Check if the index complexity_c1 exists in eval_config
            try:
                regret_value = eval_config[complexity_c1]
            except IndexError as e:
                print(f"Error: Index {complexity_c1} out of range in {eval_config_path}")
                continue

            # Save the regret value as a single param JSON
            regret_data = {'regret': regret_value}
            regret_json_path = os.path.join(sub_dir, 'regret.json')

            with open(regret_json_path, 'w') as regret_file:
                json.dump(regret_data, regret_file, indent=4)

            print(f"Successfully saved regret to {regret_json_path} with value {regret_value}")

        except Exception as e:
            print(f"Error processing directory {sub_dir}: {e}")


def evaluate_experiment_regret(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Compile regret data from multiple subdirectories into a DataFrame-like structure.
    Each unique agent type will be treated as a separate dimension in the DataFrame,
    and each episode's regret value will be stored as a single value.

    Args:
        experiment_id (str): The experiment identifier.
        experiment_signature (str): Part of the subdirectory name used to identify relevant episodes.

    Returns:
        pd.DataFrame: A DataFrame with 'episode_nr' as the index and each agent as a column with its regret value.
    """
    # Directories
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Identify the unique agent names from the subdirectory names
    agent_names = set()
    for sub_dir in sub_dirs:
        folder_name = os.path.basename(sub_dir)
        # Extract agent name from subdirectory name
        agent_name = folder_name.split(f'_{experiment_signature}_')[1].split('_config_')[0]
        agent_names.add(agent_name)

    # Store regret data for each agent in a dictionary
    agent_data = {agent: [] for agent in agent_names}

    for agent_name in agent_names:
        print(f"Processing agent: {agent_name}")

        # Filter subdirectories corresponding to this specific agent
        agent_sub_dirs = [
            sub_dir for sub_dir in sub_dirs
            if os.path.basename(sub_dir).split(f'_{experiment_signature}_')[1].split('_config_')[0] == agent_name
        ]

        for episode_nr, sub_dir in enumerate(agent_sub_dirs):
            try:
                # Load the regret data from the file
                file_path = os.path.join(sub_dir, "regret.json")
                with open(file_path, 'r') as file:
                    regret_data = json.load(file)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                continue  # Skip this subdirectory if there is an error

            # Check if regret_data contains a 'regret' value
            if 'regret' not in regret_data:
                print(f"Warning: 'regret' key not found in {file_path}")
                continue

            regret_value = regret_data['regret']

            # Store the regret data for this episode
            agent_data[agent_name].append({
                'episode_nr': episode_nr,
                'value': regret_value
            })

    # Convert agent_data into a DataFrame for each agent
    data_frames = []
    for agent_name, data in agent_data.items():
        df = pd.DataFrame(data)
        df['agent'] = agent_name  # Add agent identifier
        data_frames.append(df)

    # Concatenate all DataFrames for each agent
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Pivot the DataFrame to create a structure where 'episode_nr' is the index
    combined_df = combined_df.pivot(index='episode_nr', columns='agent', values='value')

    # Save the combined DataFrame as a CSV file
    csv_filename = "regret_values.csv"
    csv_path = os.path.join(results_dir, csv_filename)
    combined_df.to_csv(csv_path)
    print(f"Data compiled and saved to {csv_path}")

    return combined_df

def normalize_progress_each_step(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Normalize progress for each step of each episode in the experiment.
    Progress is calculated as p = 100 * (1 - (current_step_A_star_value / complexity_c1)).
    The normalized progress is saved as a new JSON file in the subdirectory of the episode.

    Args:
        experiment_id (str): The identifier for the experiment.
        experiment_signature (str): Part of the subdirectory name used to identify relevant episodes.
    """
    # Set signatures and file paths
    eval_json_files_signature = "episode_A_star_eval.json"
    config_json_files_signature = "config_*.json"
    file_signatures = [eval_json_files_signature, config_json_files_signature]

    # Get directory and file paths
    experiment_dir, results_dir = make_results_dir(experiment_id)
    sub_dirs = filter_experiment_sub_dirs(experiment_dir, experiment_signature)
    print(f"Number of subdirectories: {len(sub_dirs)}")

    for sub_dir in sub_dirs:
        try:
            # Load files matching the signatures in the subdirectory
            file_dict = bulk_load_files(sub_dir, file_signatures)

            # Load eval config
            eval_config_path = file_dict[eval_json_files_signature][0]
            with open(eval_config_path, 'r') as eval_config_file:
                eval_config = json.load(eval_config_file)

            # Load env config
            env_config_path = file_dict[config_json_files_signature][0]
            with open(env_config_path, 'r') as env_config_file:
                env_config = json.load(env_config_file)

            # Extract 'complexity_c1' from env_config
            complexity_c1 = env_config.get('complexity_c1')
            if complexity_c1 is None:
                print(f"Warning: 'complexity_c1' not found in {env_config_path}")
                continue

            # Validate that 'complexity_c1' is a valid number
            if not isinstance(complexity_c1, (int, float)) or complexity_c1 <= 0:
                print(f"Invalid 'complexity_c1' value ({complexity_c1}) in {env_config_path}")
                continue

            # Normalize each value in the A* heuristic steps
            normalized_progress = []
            for step_idx, step_value in enumerate(eval_config):
                if not isinstance(step_value, (int, float)) or step_value < 0:
                    print(f"Warning: Invalid step value ({step_value}) at index {step_idx} in {eval_config_path}")
                    continue

                # Calculate progress p = 100 * (1 - (current_step_A_star_value / complexity_c1))
                progress = 100 * (1 - (step_value / complexity_c1))

                # Ensure progress stays within bounds [0, 100]
                progress = max(0, min(100, progress))

                normalized_progress.append(progress)

            # Save the normalized progress back into the subdirectory as a new JSON file
            output_path = os.path.join(sub_dir, 'normalized_progress.json')
            with open(output_path, 'w') as output_file:
                json.dump(normalized_progress, output_file, indent=4)

            print(f"Saved normalized progress to {output_path}")

        except Exception as e:
            print(f"Error processing subdirectory {sub_dir}: {e}")


def plot_bar_plot(experiment_id, csv_file_name="cleaned_a_star_heuristic.csv", model_order=None):
    """
    Plot a bar plot showing the average of the smallest values for each model and its two versions (text and vision).

    Args:
        experiment_id (str): The experiment ID to locate the results directory.
        csv_file_name (str): The name of the CSV file to be read (default: "cleaned_a_star_heuristic.csv").
        model_order (list, optional): The desired order of models in the bar plot (default: None, which means the order will be inferred from the data).
    """
    # Load the CSV file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    csv_path = os.path.join(results_dir, csv_file_name)
    df = pd.read_csv(csv_path, header=0)

    # Extract the agent columns (ignoring episode_nr and episode_step)
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Create a DataFrame to store the average of minimum values for each agent
    summary_data = []

    for agent in agent_columns:
        # Group by 'episode_nr' and calculate the minimum heuristic value for each episode
        min_values_per_episode = df.groupby('episode_nr')[agent].min()

        # Calculate the average of these minimum values
        average_min_value = min_values_per_episode.mean()

        # Extract model name and version (text or vision) from the agent column name
        if '_text' in agent:
            model_name = agent.split('_text')[0]
            version = 'text'
        elif '_vision' in agent:
            model_name = agent.split('_vision')[0]
            version = 'vision'
        else:
            model_name = agent
            version = 'unknown'

        # Add the data to the summary list
        summary_data.append({
            'Model': model_name,
            'Version': version,
            'Average Min Value': average_min_value
        })

    # Create a DataFrame for the summary data
    summary_df = pd.DataFrame(summary_data)

    # Ensure the model order is applied correctly
    if model_order is not None:
        summary_df['Model'] = pd.Categorical(summary_df['Model'], categories=model_order, ordered=True)
    else:
        model_order = sorted(summary_df['Model'].unique())
        summary_df['Model'] = pd.Categorical(summary_df['Model'], categories=model_order, ordered=True)

    # Sort the DataFrame to ensure Seaborn uses the right order
    summary_df = summary_df.sort_values(['Model', 'Version'])

    print(f"Summary Data:\n{summary_df}\n")  # Debug print

    # Set the Seaborn style
    sns.set_style('darkgrid')

    # Create the bar plot
    plt.figure(figsize=(12, 6))
    sns.barplot(
        x='Model',
        y='Average Min Value',
        hue='Version',
        data=summary_df,
        order=model_order,  # Order for the x-axis
        hue_order=['text', 'vision'],  # Order for the hues
        palette='viridis'
    )

    # Set the plot title and labels
    plt.title('Average of Minimum A* Heuristic Values Per Episode')
    plt.xlabel('Model')
    plt.ylabel('Average Minimum Value')

    # Place the legend
    plt.legend(title='Version', loc='upper right')

    # Save the plot to the results directory
    plot_path = os.path.join(results_dir, 'a_star_heuristic_barplot.png')
    plt.savefig(plot_path, bbox_inches='tight')

    # Show the plot
    plt.show()

    print(f"Bar plot saved at {plot_path}")


def plot_heat_map(experiment_id, cleaned_csv="cleaned_a_star_heuristic.csv", regret_csv="regret_values.csv"):
    """
    Loads the cleaned A* heuristic and regret CSVs, and plots heatmaps for each agent_setting.
    The heatmaps display the regret and the minimum A* heuristic values for each episode and step.

    Args:
        experiment_id (str): The experiment identifier to locate the results directory.
        cleaned_csv (str): The name of the CSV file containing cleaned A* heuristic data (default: "cleaned_a_star_heuristic.csv").
        regret_csv (str): The name of the CSV file containing regret data (default: "regret_values.csv").
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)

    # Load the two CSV files
    cleaned_path = os.path.join(results_dir, cleaned_csv)
    regret_path = os.path.join(results_dir, regret_csv)
    cleaned_df = pd.read_csv(cleaned_path, header=0)
    regret_df = pd.read_csv(regret_path, header=0)

    # Extract agent names from column names (ignore episode columns like episode_nr, episode_step)
    agent_columns_cleaned = [col for col in cleaned_df.columns if col not in ['episode_nr', 'episode_step']]
    agent_columns_regret = [col for col in regret_df.columns if col != 'episode_nr']

    for agent in agent_columns_cleaned:
        print(f"Processing heatmaps for agent: {agent}")

        # Step 1: Heatmap for the minimum A* heuristic values
        a_star_data = cleaned_df.groupby('episode_nr')[agent].min().reset_index()

        # Pivot to a 2D heatmap format (episode_nr as index, step as columns)
        a_star_heatmap_data = cleaned_df.pivot(index='episode_nr', columns='episode_step', values=agent)

        # Plot the heatmap for A* heuristic
        plt.figure(figsize=(12, 6))
        sns.heatmap(a_star_heatmap_data, cmap='viridis', cbar=True)
        plt.title(f'Minimum A* Heuristic Heatmap for {agent}')
        plt.xlabel('Step')
        plt.ylabel('Episode')
        plot_path = os.path.join(results_dir, f'heatmap_a_star_{agent}.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"A* heuristic heatmap saved at {plot_path}")

        # Step 2: Heatmap for the regret values
        if agent in agent_columns_regret:
            regret_data = regret_df[['episode_nr', agent]].copy()

            # Pivot to a 2D heatmap format (episode_nr as index, step as columns)
            regret_heatmap_data = regret_data.pivot(index='episode_nr', columns=None, values=agent)

            # Plot the heatmap for regret values
            plt.figure(figsize=(12, 6))
            sns.heatmap(regret_heatmap_data, cmap='magma', cbar=True)
            plt.title(f'Regret Heatmap for {agent}')
            plt.xlabel('Regret Value')
            plt.ylabel('Episode')
            plot_path = os.path.join(results_dir, f'heatmap_regret_{agent}.png')
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
            print(f"Regret heatmap saved at {plot_path}")


def plot_heat_map(experiment_id, cleaned_csv="cleaned_a_star_heuristic.csv", regret_csv="regret_values.csv"):
    """
    Loads the cleaned A* heuristic and regret CSVs, and plots a 7x7 heatmap.
    Each cell in the heatmap corresponds to the minimum A* heuristic or regret value
    for a given number of geoms and shortest path solution.

    Args:
        experiment_id (str): The experiment identifier to locate the results directory.
        cleaned_csv (str): The name of the CSV file containing cleaned A* heuristic data.
        regret_csv (str): The name of the CSV file containing regret data.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)

    # Load the CSV files
    cleaned_path = os.path.join(results_dir, cleaned_csv)
    regret_path = os.path.join(results_dir, regret_csv)
    cleaned_df = pd.read_csv(cleaned_path, header=0)
    regret_df = pd.read_csv(regret_path, header=0)

    # Extract agent names from column names (ignore episode columns like episode_nr, episode_step)
    agent_columns_cleaned = [col for col in cleaned_df.columns if col not in ['episode_nr', 'episode_step']]
    agent_columns_regret = [col for col in regret_df.columns if col != 'episode_nr']

    # We assume that there are 49 episodes, corresponding to a 7x7 grid
    grid_size = 7

    for agent in agent_columns_cleaned:
        print(f"Processing heatmaps for agent: {agent}")

        # Step 1: Heatmap for the minimum A* heuristic values
        a_star_min_values = cleaned_df.groupby('episode_nr')[agent].min().reset_index()

        # Check if the number of episodes is 49
        num_episodes = a_star_min_values.shape[0]
        if num_episodes != grid_size ** 2:
            print(
                f"Warning: Expected {grid_size ** 2} episodes, but found {num_episodes}. Check the dataset for missing data.")

        # Reshape to 7x7 format (assuming 49 episodes)
        a_star_values_reshaped = a_star_min_values[agent].values.reshape((grid_size, grid_size))

        # Plot the heatmap for A* heuristic
        plt.figure(figsize=(10, 8))
        sns.heatmap(a_star_values_reshaped, annot=True, fmt=".2f", cmap='viridis_r', cbar=True)
        plt.title(f'Minimum A* Heuristic for {agent}')
        plt.xlabel('Number of Geoms')
        plt.ylabel('Shortest Path Length')
        plt.xticks(ticks=[i + 0.5 for i in range(grid_size)], labels=[f'{i + 1}' for i in range(grid_size)])
        plt.yticks(ticks=[i + 0.5 for i in range(grid_size)], labels=[f'{i + 1}' for i in range(grid_size)], rotation=0)
        plot_path = os.path.join(results_dir, f'heatmap_a_star_{agent}.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"A* heuristic heatmap saved at {plot_path}")

        # Step 2: Heatmap for the regret values
        if agent in agent_columns_regret:
            regret_values = regret_df[['episode_nr', agent]].copy()

            # Use the minimum regret value for each episode
            regret_min_values = regret_values.groupby('episode_nr')[agent].min().reset_index()

            # Reshape to 7x7 format (assuming 49 episodes)
            regret_values_reshaped = regret_min_values[agent].values.reshape((grid_size, grid_size))

            # Plot the heatmap for regret values
            plt.figure(figsize=(10, 8))
            sns.heatmap(regret_values_reshaped, annot=True, fmt=".2f", cmap='magma_r', cbar=True)
            plt.title(f'Regret Heatmap for {agent}')
            plt.xlabel('Number of Geoms')
            plt.ylabel('Shortest Path Length')
            plt.xticks(ticks=[i + 0.5 for i in range(grid_size)], labels=[f'{i + 1}' for i in range(grid_size)])
            plt.yticks(ticks=[i + 0.5 for i in range(grid_size)], labels=[f'{i + 1}' for i in range(grid_size)],
                       rotation=0)
            plot_path = os.path.join(results_dir, f'heatmap_regret_{agent}.png')
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
            print(f"Regret heatmap saved at {plot_path}")


def evaluate_experiment_normalized_progress(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Compile normalized progress data from multiple subdirectories into a 3D DataFrame-like structure.
    Each unique agent type will be treated as a separate dimension in the DataFrame,
    and each episode's raw progress data will be kept without averaging.

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
        # Extract the agent name
        agent_name = folder_name.split(f'_{experiment_signature}_')[1].split('_config_')[0]
        agent_names.add(agent_name)

    # Store data for each agent in a dictionary
    agent_data = {agent: [] for agent in agent_names}

    for agent_name in agent_names:
        print(f"Processing agent: {agent_name}")

        # Filter subdirectories corresponding to this specific agent
        agent_sub_dirs = [
            sub_dir for sub_dir in sub_dirs
            if os.path.basename(sub_dir).split(f'_{experiment_signature}_')[1].split('_config_')[0] == agent_name
        ]

        for episode_nr, sub_dir in enumerate(agent_sub_dirs):
            try:
                # Load the normalized progress data from the file
                file_path = os.path.join(sub_dir, "normalized_progress.json")
                with open(file_path, 'r') as file:
                    normalized_progress = json.load(file)
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
                continue  # Skip this subdirectory if there is an error

            # Check if normalized_progress is valid
            if not isinstance(normalized_progress, list):
                print(f"Invalid data in {file_path}: not a list")
                continue

            # Store the normalized progress data for this episode
            for step_idx, progress_value in enumerate(normalized_progress):
                agent_data[agent_name].append({
                    'episode_nr': episode_nr,
                    'episode_step': step_idx,
                    'value': progress_value
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
    csv_filename = "normalized_progress.csv"
    csv_path = os.path.join(results_dir, csv_filename)
    combined_df.to_csv(csv_path)
    print(f"Data compiled and saved to {csv_path}")

    return combined_df

def plot_csv_with_confidence_interval(experiment_id, csv_file_name="cleaned_normalized_progress.csv", show_confidence_interval=False):
    """
    Reads a CSV file with normalized progress data, processes the data, and plots two separate line graphs:
    - One for all agents in the **vision** scenario
    - One for all agents in the **text** scenario

    Args:
        experiment_id (str): The experiment ID to locate the results directory.
        csv_file_name (str): The name of the CSV file to be read (default: 'cleaned_normalized_progress.csv').
        show_confidence_interval (bool): If True, plot shaded error bands (mean ± std) for each agent. Default is True.
    """
    # Load the CSV file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    csv_path = os.path.join(results_dir, csv_file_name)
    df = pd.read_csv(csv_path, header=0)

    # Extract columns corresponding to agents
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Split agents into vision and text scenarios
    vision_agents = [col for col in agent_columns if '_vision' in col]
    text_agents = [col for col in agent_columns if '_text' in col]

    ## --- Plot for **Vision Scenario** ---
    plt.figure(figsize=(18, 6))
    sns.set_style('darkgrid')

    for agent in vision_agents:
        grouped_df = df.groupby('episode_step')[agent]
        means = grouped_df.mean()
        std_devs = grouped_df.std()
        x_values = means.index

        # Plot the mean line for this agent
        plt.plot(x_values, means, label=f"{agent}", linestyle='-', linewidth=2)

        if show_confidence_interval:
            # Plot the shaded area as the error band (mean ± std)
            plt.fill_between(x_values, means - std_devs, means + std_devs, alpha=0.2)

    plt.xlabel('Step')
    plt.ylabel('Normalized Progress (%)')
    plt.title('Average Normalized Progress for Vision Agents')
    plt.figtext(0.5, -0.05, 'This plot shows the average normalized progress (0-100%) for vision agents at each step',
                ha='center', va='center', fontsize=10, style='italic')
    plt.legend(title="Agent", loc="lower right")

    # Save the vision plot
    vision_plot_path = os.path.join(results_dir, f"normalized_progress_evaluation_vision.png")
    plt.savefig(vision_plot_path, bbox_inches='tight')
    plt.show()
    print(f"Vision plot saved to {vision_plot_path}")

    ## --- Plot for **Text Scenario** ---
    plt.figure(figsize=(18, 6))
    sns.set_style('darkgrid')

    for agent in text_agents:
        grouped_df = df.groupby('episode_step')[agent]
        means = grouped_df.mean()
        std_devs = grouped_df.std()
        x_values = means.index

        # Plot the mean line for this agent
        plt.plot(x_values, means, label=f"{agent}", linestyle='-', linewidth=2)

        if show_confidence_interval:
            # Plot the shaded area as the error band (mean ± std)
            plt.fill_between(x_values, means - std_devs, means + std_devs, alpha=0.2)

    plt.xlabel('Step')
    plt.ylabel('Normalized Progress (%)')
    plt.title('Average Normalized Progress for Text Agents')
    plt.figtext(0.5, -0.05, 'This plot shows the average normalized progress (0-100%) for text agents at each step',
                ha='center', va='center', fontsize=10, style='italic')
    plt.legend(title="Agent", loc="lower right")

    # Save the text plot
    text_plot_path = os.path.join(results_dir, f"normalized_progress_evaluation_text.png")
    plt.savefig(text_plot_path, bbox_inches='tight')
    plt.show()
    print(f"Text plot saved to {text_plot_path}")



def plot_csv_with_confidence_interval_per_agent(experiment_id, csv_file_name="cleaned_normalized_progress.csv", show_confidence_interval=True):
    """
    Reads a CSV file with normalized progress data, processes the data, and plots separate line graphs for each agent type.
    Each plot contains the "text" and "vision" versions of that agent.

    Args:
        experiment_id (str): The experiment ID to locate the results directory.
        csv_file_name (str): The name of the CSV file to be read (default: 'cleaned_normalized_progress.csv').
        show_confidence_interval (bool): If True, plot shaded error bands (mean ± std) for each agent. Default is True.
    """
    # Load the CSV file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    csv_path = os.path.join(results_dir, csv_file_name)
    df = pd.read_csv(csv_path, header=0)

    # Extract columns corresponding to agents
    agent_columns = [col for col in df.columns if col not in ['episode_nr', 'episode_step']]

    # Extract unique agent types (Claude, Gemini, etc.) by removing the "_text" and "_vision" suffix
    agent_types = sorted({col.split('_')[0] for col in agent_columns})

    ## --- Plot for each agent type (e.g., Claude, Gemini) ---
    for agent_type in agent_types:
        # Filter columns for the current agent (both text and vision versions)
        agent_text = f"{agent_type}_text"
        agent_vision = f"{agent_type}_vision"
        agents_to_plot = [col for col in agent_columns if col in [agent_text, agent_vision]]

        if not agents_to_plot:
            print(f"No data available for agent type: {agent_type}")
            continue

        plt.figure(figsize=(18, 6))
        sns.set_style('darkgrid')

        for agent in agents_to_plot:
            grouped_df = df.groupby('episode_step')[agent]
            means = grouped_df.mean()
            std_devs = grouped_df.std()
            x_values = means.index

            # Plot the mean line for this agent (text or vision version)
            plt.plot(x_values, means, label=f"{agent}", linestyle='-', linewidth=2)

            if show_confidence_interval:
                # Plot the shaded area as the error band (mean ± std)
                plt.fill_between(x_values, means - std_devs, means + std_devs, alpha=0.2)

        # Set the plot details
        plt.xlabel('Step')
        plt.ylabel('Normalized Progress (%)')
        plt.title(f'Average Normalized Progress for Agent: {agent_type.capitalize()} (Text vs Vision)')
        plt.figtext(0.5, -0.05, f'This plot shows the average normalized progress (0-100%) for {agent_type.capitalize()} at each step',
                    ha='center', va='center', fontsize=10, style='italic')
        plt.legend(title="Version", loc="lower right")

        # Save the plot for this agent
        agent_plot_path = os.path.join(results_dir, f"normalized_progress_evaluation_{agent_type}.png")
        plt.savefig(agent_plot_path, bbox_inches='tight')
        plt.show()
        print(f"Plot for agent type '{agent_type}' saved at {agent_plot_path}")


if __name__ == "__main__":

    experiment_id = 'evaluate_Berkeley'
    custom_order = ['Claude', 'Gemini', 'GPT-4', 'InternVL']
    plot_bar_plot(experiment_id=experiment_id, model_order=custom_order)
    #reduce_episode_data(experiment_id)
    #evaluate_experiment_regret(experiment_id)
    #plot_bar_plot_regret(experiment_id=experiment_id, model_order=custom_order)

    #plot_heat_map(experiment_id=experiment_id)

    #normalize_progress_each_step(experiment_id)
    #evaluate_experiment_normalized_progress(experiment_id)

    #clean_and_process_normalized_progress(experiment_id)
    #plot_csv_with_confidence_interval(experiment_id)
    #plot_csv_with_confidence_interval_per_agent(experiment_id)