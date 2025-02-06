import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")

def plot_heat_map_episode_level_average(
    experiment_id, compiled_csv="episode_outcomes_evaluation.csv",
    model_types=None, representation_types=None
):
    """
    Loads the compiled evaluation CSV and generates averaged heatmaps for specified model types and representation types.
    Averages metrics (min_path_length, spl_value, won, won_at_spl) across model types and representation types.

    Args:
        experiment_id (str): The experiment identifier to locate the results directory.
        compiled_csv (str): The name of the CSV file containing the compiled episode-level evaluation data.
        model_types (list): List of model types to average over. If None, all model types are used.
        representation_types (list): List of representation types to average over. If None, all representation types are used.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    heatmap_dir = os.path.join(results_dir, 'heatmaps_average')  # Subdirectory for averaged heatmaps
    os.makedirs(heatmap_dir, exist_ok=True)

    # Load the compiled evaluation CSV
    compiled_path = os.path.join(results_dir, compiled_csv)
    eval_df = pd.read_csv(compiled_path)

    # Verify necessary columns
    required_columns = ['episode_nr', 'model_type', 'representation_type', 'min_path_length', 'spl_value',
                        'won', 'won_at_spl', 'num_geoms', 'complexity_c1']
    if not all(col in eval_df.columns for col in required_columns):
        raise ValueError("The compiled CSV is missing required columns.")

    # Filter by model types if specified
    if model_types:
        eval_df = eval_df[eval_df['model_type'].isin(model_types)]

    # Filter by representation types if specified
    if representation_types:
        eval_df = eval_df[eval_df['representation_type'].isin(representation_types)]

    if eval_df.empty:
        print("No data found for the specified model types or representation types.")
        return

    # Metrics to plot
    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']

    # Determine unique ranges of num_geoms and complexity_c1
    geom_range = sorted(eval_df['num_geoms'].unique())
    c1_range = sorted(eval_df['complexity_c1'].unique())

    grid_width = len(geom_range)
    grid_height = len(c1_range)

    for metric in metrics:
        # Pivot and average data across model types/representation types
        heatmap_data = (
            eval_df.groupby(['num_geoms', 'complexity_c1'])[metric]
            .mean()
            .unstack(level=0)  # num_geoms become columns
            .reindex(index=c1_range, columns=geom_range, fill_value=0)
        )

        # Plot the heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(heatmap_data, annot=True, fmt=".2f",
                    cmap='viridis_r')# if metric in ['min_path_length', 'spl_value'] else 'magma', cbar=True) #don't like magma

        plt.gca().invert_yaxis()

        plt.title(f'Averaged {metric.replace("_", " ").capitalize()} Heatmap\n'
                  f'Model Types: {", ".join(model_types) if model_types else "All"} | '
                  f'Representation Types: {", ".join(representation_types) if representation_types else "All"}')
        plt.xlabel('Number of Geoms')
        plt.ylabel('Shortest Path Length (c1)')

        # Set xticks and yticks to align with data ranges
        plt.xticks(ticks=[i + 0.5 for i in range(grid_width)], labels=[str(g) for g in geom_range])
        plt.yticks(ticks=[i + 0.5 for i in range(grid_height)], labels=[str(c) for c in c1_range], rotation=0)

        # Save the plot to the subdirectory
        model_part = '_'.join(model_types) if model_types else 'All'
        representation_part = '_'.join(representation_types) if representation_types else 'All'
        plot_path = os.path.join(heatmap_dir, f'heatmap_avg_{metric}_{model_part}_{representation_part}.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"Averaged {metric.replace('_', ' ').capitalize()} heatmap saved at {plot_path}")


if __name__ == "__main__":

    experiment_id = 'random baseline'
    model_types = ['rand-AI-invalid', 'rand-AI-valid']  # Update to use model_types
    representation_types = ['text']  # Update to use representation_types

    # Evaluate and plot for each episode of the experiment
    plot_heat_map_episode_level_average(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=representation_types
    )
