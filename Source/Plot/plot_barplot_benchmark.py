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


def plot_bar_plot_with_ci(experiment_id, model_types=None, representation_types=None, baseline_model_types=None,
                          text_size=19):
    # Set result directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    plots_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id, 'bar_plots_with_baselines')
    os.makedirs(plots_dir, exist_ok=True)

    # Load data
    df, baseline_df, stats_df = load_dfs(experiment_id, model_types=model_types, representation_types=representation_types, baseline_model_types=baseline_model_types)

    # Define metrics to plot
    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']

    # Convert the 'won' metric to percentages (0-100)
    # Convert 'won' to percentages for both main and baseline data
    if 'won' in df.columns:
        df['won'] *= 100
    if 'won' in baseline_df.columns:
        baseline_df['won'] *= 100

    # Update metric_titles to reflect the change
    metric_titles = {
        'min_path_length': 'Average Minimum Path Length',
        'spl_value': 'Mean Step-Deviation from Optimal Path',
        'won': 'Completed Episodes (%)',  # Add percentage sign
        'won_at_spl': 'Win at SPL Percentage (%)'
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

        # Rename representation_type values
        representation_rename_dict = {
            "text": "Text",
            "vision": "Vision 3D",
            "schematic": "Vision 2D"
        }

        if representation_rename_dict:
            filtered_df['representation_type'] = filtered_df['representation_type'].astype(str).replace(
                representation_rename_dict)
            representation_types_renamed = [representation_rename_dict.get(r, r) for r in representation_types]
        else:
            representation_types_renamed = representation_types

        # Rename model_type values
        model_rename_dict = {
            'rand-AI-valid': 'Random AI',
            'optimal-AI': 'Optimal AI',
            'claude-3-5-sonnet-20241022': 'Sonnet-3.5',
            'gemini-2.0-flash-exp': 'Gemini-2.0-flash',
            'Qwen2-VL-72B-Instruct-GPTQ-Int4': 'Qwen2-72B-int4',
            'Qwen2-VL-72B-Instruct': 'Qwen2-72B',
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

        # Create the bar plot with dynamic confidence intervals
        plt.figure(figsize=(24, 6.2))
        bar_plot = sns.barplot(
            x='model_type',
            y=metric,
            hue='representation_type',
            data=filtered_df,
            order=model_types_renamed,
            hue_order=representation_types_renamed,
            palette='viridis',
            errorbar=('ci', 95),  # Let Seaborn calculate 95% confidence intervals
            capsize=0.1
        )

        if metric == 'min_path_length' or metric == 'spl_value':
            label_offset = 0.33
        elif metric == 'won_at_spl' or metric == 'won':
            label_offset = 5  # Adjust for percentage scale

        # Add labels on top of each bar
        for bar in bar_plot.patches:
            bar_height = bar.get_height()  # Get bar height
            if not np.isnan(bar_height) and bar_height > 0.0:  # Only add labels for valid and non-zero bars
                bar_x = bar.get_x() + bar.get_width() / 2
                bar_plot.annotate(
                    f'{bar_height:.2f}',  # Format the number
                    (bar_x, bar_height + label_offset),  # Position slightly above the bar
                    ha='center', va='bottom', fontsize=15, color='black'
                )


        # Calculate baseline averages
        baseline_avg = (
            baseline_df.groupby(['model_type', 'representation_type'])[metric]
            .mean()
            .reset_index()
            .rename(columns={metric: f'Baseline {metric}'})
        )

        if metric == 'min_path_length' or metric == 'spl_value':
            # Manually set the optimal-AI baseline value
            manual_optimal_value = 0.33
            baseline_avg.loc[baseline_avg["model_type"] == "optimal-AI", f"Baseline {metric}"] = manual_optimal_value

        # Overlay baseline horizontal lines
        for _, row in baseline_avg.iterrows():
            if row["model_type"] == 'rand-AI-valid':
                b_label = 'random'
                b_color = 'red'
                set_linestyle = (0, (5, 5))  # Dashed line (5 pixels on, 5 pixels off)
                line_thickness = 1.5  # Increased thickness

            elif row["model_type"] == 'optimal-AI':
                b_label = 'human'
                b_color = '#14213d'
                set_linestyle = (0, (10, 5))  # Dotted line (1 pixel on, 1 pixel off)
                line_thickness = 2  # Even thicker for emphasis

            plt.axhline(
                y=row[f'Baseline {metric}'],
                color=b_color,
                linestyle=set_linestyle,
                linewidth=line_thickness,
                label=f'baseline: {b_label}'
            )


        # Set the plot title and labels
        #plt.title(f'{metric_titles[metric]} Per Model (Baseline Overlay)')
        plt.xlabel('')
        plt.ylabel(metric_titles[metric])
        plt.tick_params(axis='y', labelsize=text_size - 4)
        plt.xlabel('', fontsize=text_size)  # Set x-axis label size (increase to 14 or desired size)
        plt.ylabel(metric_titles[metric], fontsize=text_size)  # Set y-axis label size


        # Rotate x-axis labels and adjust font size
        plt.xticks(rotation=0, fontsize=text_size)  # Adjust font size for model names (x-axis labels)

        # Get handles and labels for the legend
        handles, labels = bar_plot.get_legend_handles_labels()

        # Place the legend on top with one row
        plt.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, 1.15),
            ncol=len(labels),  # Ensure all labels fit in one row
            frameon=False,
            fontsize=text_size - 2
        )
        if metric == 'won_at_spl' or metric == 'won':
            pass
        elif metric == 'min_path_length' or metric == 'spl_value':
            # Ensure no legend is displayed
            #plt.legend([], [], frameon=False)
            pass

        # Save the plot to the subdirectory
        plot_path = os.path.join(plots_dir, f"barplot_{metric}_with_baselines_and_ci.png")
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"{metric_titles[metric]} plot saved at {plot_path}")

        # Print values for the bar plot in the console
        print(f"\n{metric_titles[metric]}:")
        for model in model_types_renamed:
            # Extract mean and values for each representation type
            mean_value = filtered_df.loc[filtered_df['model_type'] == model, metric].mean()
            vision_2d_value = filtered_df.loc[
                (filtered_df['model_type'] == model) &
                (filtered_df['representation_type'] == 'Vision 2D'),
                metric
            ].mean()
            vision_3d_value = filtered_df.loc[
                (filtered_df['model_type'] == model) &
                (filtered_df['representation_type'] == 'Vision 3D'),
                metric
            ].mean()
            text_value = filtered_df.loc[
                (filtered_df['model_type'] == model) &
                (filtered_df['representation_type'] == 'Text'),
                metric
            ].mean()

            # Print in the specified format
            print(f"{model} & {mean_value:.2f} & {vision_3d_value:.2f} & {vision_2d_value:.2f} & {text_value:.2f}")


if __name__ == "__main__":

    experiment_id = 'ICML_all'
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'InternVL', 'llavaonevision-72B', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']#, 'Qwen2-VL-72B-Instruct']
    representation_types = ['vision', 'schematic', 'text']  # Specify the representation types
    baseline_agents = ['rand-AI-valid', 'optimal-AI']

    # Evaluate and plot for each episode of the experiment
    plot_bar_plot_with_ci(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=representation_types,
        baseline_model_types=baseline_agents
    )
