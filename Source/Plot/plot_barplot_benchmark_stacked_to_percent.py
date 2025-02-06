import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from itertools import product

# Set the Seaborn style
sns.set_style('darkgrid')

def load_dfs(experiment_id, model_types=None, representation_types=None, baseline_model_types=None):
    # Set result directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)

    # Data file paths
    eval_csv_path = os.path.join(results_dir, 'episode_outcomes_evaluation.csv')
    baseline_csv_path = os.path.join(results_dir, 'baselines.csv')
    stats_csv_path = os.path.join(results_dir, 'experiment_statistics_evaluation.csv')

    # Load dataframes
    df = pd.read_csv(eval_csv_path, header=0)
    baseline_df = pd.read_csv(baseline_csv_path, header=0)
    stats_df = pd.read_csv(stats_csv_path, header=0)

    # Filter main data by model types and representation types if specified
    if model_types:
        df = df[df['model_type'].isin(model_types)]
        stats_df = stats_df[stats_df['model_type'].isin(df['model_type'].unique())]

    if representation_types:
        df = df[df['representation_type'].isin(representation_types)]
        stats_df = stats_df[stats_df['representation_type'].isin(df['representation_type'].unique())]

    # Filter baseline data by baseline model types and representation types if specified
    if baseline_model_types:
        baseline_df = baseline_df[baseline_df['model_type'].isin(baseline_model_types)]

    if df.empty:
        print("No data found for the specified model types or representation types.")
        return

    return df, baseline_df, stats_df


def plot_stacked_bar_plot_with_ci(experiment_id, model_types=None, representation_types=None, baseline_model_types=None, text_size=18):
    # Set result directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    plots_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id, 'stacked_bar_plots')
    os.makedirs(plots_dir, exist_ok=True)

    # Load data
    df, baseline_df, stats_df = load_dfs(experiment_id, model_types=model_types, representation_types=representation_types, baseline_model_types=baseline_model_types)

    # Define metrics to plot
    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']
    metric_titles = {
        'min_path_length': 'Average Minimum Path Length',
        'spl_value': 'Mean Step-Deviation from Optimal Path',
        'won': 'Completed Episodes (%)',
        'won_at_spl': 'Win at SPL Percentage'
    }

    for metric in metrics:
        # Filter the main data for the current metric
        filtered_df = df[['model_type', 'representation_type', metric]].dropna()

        # Ensure model_type is ordered according to model_types
        if model_types:
            filtered_df['model_type'] = pd.Categorical(
                filtered_df['model_type'],
                categories=model_types,
                ordered=True
            )

        # Ensure representation_type is ordered according to representation_types
        if representation_types:
            filtered_df['representation_type'] = pd.Categorical(
                filtered_df['representation_type'],
                categories=representation_types,
                ordered=True
            )

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

        if model_rename_dict:
            filtered_df['model_type'] = filtered_df['model_type'].astype(str).replace(model_rename_dict)
            model_types_renamed = [model_rename_dict.get(m, m) for m in model_types]

            filtered_df['model_type'] = pd.Categorical(
                filtered_df['model_type'],
                categories=model_types_renamed,
                ordered=True
            )

        # Calculate stacked bar plot values
        stacked_data = filtered_df.pivot_table(
            index='model_type',
            columns='representation_type',
            values=metric,
            aggfunc='mean',
            fill_value=0
        )
        stacked_data = stacked_data[representation_types]  # Ensure columns are ordered by representation_types

        # Normalize the stacked data so that total reflects an average
        stacked_data = stacked_data.div(len(representation_types), axis=1)

        # Plot stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 9))
        bottom = np.zeros(len(stacked_data))  # Initialize bottom for stacking
        colors = sns.color_palette('viridis', len(representation_types))

        for i, rep_type in enumerate(representation_types):
            ax.bar(
                stacked_data.index,
                stacked_data[rep_type],
                bottom=bottom,
                label=rep_type,
                color=colors[i],
                edgecolor='black'
            )
            bottom += stacked_data[rep_type]  # Update bottom for next stack

        # Add baseline horizontal lines
        for _, row in baseline_df.groupby(['model_type', 'representation_type'])[metric].mean().reset_index().iterrows():
            if row['model_type'] in model_types_renamed:
                baseline_value = row[metric]
                model_index = model_types_renamed.index(row['model_type'])
                color = 'red' if row['model_type'] == 'Random AI' else '#1E90FF'
                ax.hlines(
                    y=baseline_value,
                    xmin=model_index - 0.4,
                    xmax=model_index + 0.4,
                    colors=color,
                    linestyles='--',
                    label=f"{row['representation_type']} baseline" if i == 0 else None
                )

        # Annotate the total values on top of each bar
        for i, model in enumerate(stacked_data.index):
            total_value = stacked_data.loc[model].sum()
            ax.text(i, total_value + 0.002, f'{total_value * 100:.1f}%', ha='center', va='bottom', fontsize=text_size)

        # Create a dictionary for renaming legend labels
        legend_rename_dict = {
            "text": "text",
            "vision": "vision 3D",
            "schematic": "vision 2D",
        }

        # Get current legend handles and labels
        handles, labels = ax.get_legend_handles_labels()

        # Replace labels using the dictionary
        labels = [legend_rename_dict.get(label, label) for label in labels]

        # Add updated legend
        ax.legend(handles, labels, title="", fontsize=text_size, title_fontsize=18)

        # Customize plot
        ax.set_ylabel(metric_titles[metric], fontsize=text_size+4)
        ax.tick_params(axis='y', labelsize=text_size-2)  # Increase y-axis tick label size to 14 (or desired size)
        ax.set_xlabel('', fontsize=text_size)
        ax.set_xticks(range(len(stacked_data)))
        ax.set_xticklabels(stacked_data.index, fontsize=text_size-2, rotation=45)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y * 100:.0f}%'))  # Format y-axis as percentages

        # Save the plot
        plot_path = os.path.join(plots_dir, f"stacked_bar_plot_{metric}.png")
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close(fig)
        print(f"{metric_titles[metric]} stacked bar plot saved at {plot_path}")




if __name__ == "__main__":

    experiment_id = 'ICML_all'
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'InternVL', 'llavaonevision-72B', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']
    representation_types = ['vision', 'schematic', 'text']  # Specify the representation types
    baseline_agents = ['rand-AI-valid', 'optimal-AI']

    # Evaluate and plot for each episode of the experiment
    plot_stacked_bar_plot_with_ci(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=representation_types,
        baseline_model_types=baseline_agents
    )
