import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Set up Seaborn
sns.set_style('darkgrid')

def plot_csv_with_confidence_interval(experiment_id, csv_file_name="episode_steps_evaluation.csv",
                                      agents=None, modalities=None, show_confidence_interval=True, text_size=18):
    """
    Reads a CSV file with evaluation data and plots separate line graphs for:
    - Move Heuristics
    - Regret
    - Normalized Progress

    Plots each agent with all modalities averaged if no modality is specified.

    Args:
        experiment_id (str): The experiment ID to locate the results directory.
        csv_file_name (str): The name of the CSV file to be read (default: 'evaluation_compiled.csv').
        agents (list): List of agent names to filter. If None, all agents are used.
        modalities (list): List of modalities to filter. If None, averages over all modalities.
        show_confidence_interval (bool): If True, plot shaded error bands (mean ± std) for each agent.
        text_size (int): Font size for all text elements in the plots.
    """
    # Set text size for all plot elements
    plt.rcParams.update({
        'font.size': text_size,
        'axes.titlesize': text_size + 6,
        'axes.labelsize': text_size,
        'xtick.labelsize': text_size - 2,
        'ytick.labelsize': text_size - 2,
        'legend.fontsize': text_size - 2,
        'figure.titlesize': text_size + 4
    })

    # Load the CSV file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)

    # Create subdirectory for plots
    plots_dir = os.path.join(results_dir, 'steps_line_plots')
    os.makedirs(plots_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, csv_file_name)
    df = pd.read_csv(csv_path, header=0)

    # Apply filters if agents are specified
    if agents:
        df = df[df['model_type'].isin(agents)]

    if df.empty:
        print("No data found for the specified agents.")
        return

    # Handle modalities
    if modalities:
        df = df[df['representation_type'].isin(modalities)]
        if df.empty:
            print("No data found for the specified modalities.")
            return
    else:
        # Average over all modalities
        numeric_cols = df.select_dtypes(include=['number']).columns
        df = df.groupby(['model_type', 'episode_step'], as_index=False)[numeric_cols].mean()

    # Define metrics to plot
    metrics = ['move_heuristics', 'regret', 'normalized_progress']
    metric_titles = {
        'move_heuristics': 'Shortest Path to Goal State',
        'regret': 'Regret (Excess Moves)',
        'normalized_progress': 'Normalized Progress (%)'
    }

    # Rename model_type values
    model_rename_dict = {
        'rand-AI-valid': 'Random AI',
        'optimal-AI': 'Optimal AI',
        'claude-3-5-sonnet-20241022': 'Sonnet-3.5',
        'gemini-2.0-flash-exp': 'Gemini-2.0-flash',
        'Qwen2-VL-72B-Instruct-GPTQ-Int4': 'Qwen2-72B',
        'gpt-4o': 'GPT-4o',
        'llavaonevision-72B': 'LLaVA-OneVision-72B',
        'InternVL': 'InternVL2.5-78B'
    }
    filtered_df = df
    if model_rename_dict:
        filtered_df['model_type'] = filtered_df['model_type'].astype(str).replace(model_rename_dict)
        model_types_renamed = [model_rename_dict.get(m, m) for m in model_types]

        filtered_df['model_type'] = pd.Categorical(
            filtered_df['model_type'],
            categories=model_types_renamed,
            ordered=True
        )

    # Loop through each metric and create plots
    for metric in metrics:
        plt.figure(figsize=(24, 6))

        # Group by agent to create one line per agent
        for agent, agent_df in filtered_df.groupby('model_type'):
            grouped_df = agent_df.groupby('episode_step')[metric]

            # Calculate mean and std for each step
            means = grouped_df.mean()
            std_devs = grouped_df.std()
            x_values = means.index

            # Plot the mean line
            plt.plot(x_values, means, label=agent, linestyle='-', linewidth=2)

            if show_confidence_interval:
                # Plot the shaded area (mean ± std)
                plt.fill_between(x_values, means - std_devs, means + std_devs, alpha=0.2)

        # Set axis limits
        plt.ylim(bottom=0)  # y-axis starts at 0
        plt.xlim(left=0, right=20)  # x-axis includes 20 as the last value
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True, min_n_ticks=1))

        # Label the plot
        plt.xlabel('Episode Steps')
        plt.ylabel(metric_titles[metric])
        plt.legend(title="", loc="lower left")

        # Save the plot to the subdirectory
        agent_part = '_'.join(agents) if agents else 'All'
        modality_part = '_'.join(modalities) if modalities else 'AllModalitiesAveraged'
        plot_path = os.path.join(plots_dir, f"{metric}_evaluation_{agent_part}_{modality_part}.png")
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"{metric_titles[metric]} plot saved to {plot_path}")



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'InternVL', 'llavaonevision-72B', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']
    representation_types = ['schematic']#, 'vision', 'text']  # Specify the representation types

    # Evaluate and plot for each episode of the experiment
    plot_csv_with_confidence_interval(
        experiment_id=experiment_id,
        agents=model_types,
        show_confidence_interval=True
    )
