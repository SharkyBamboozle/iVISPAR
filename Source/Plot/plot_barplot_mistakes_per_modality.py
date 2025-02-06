import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set the Seaborn style
sns.set_style('darkgrid')

palette = ["#13315c", "#3d5a80", "#98c1d9", "#ee6c4d", "#ff4800"]

def plot_cumulative_bar_plot_per_modality_with_ci(experiment_id, representation_types=None, text_size=22, label_offset=0.2):
    # Set result directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    plots_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id, 'mistakes')
    os.makedirs(plots_dir, exist_ok=True)

    # Load data
    df = pd.read_csv(os.path.join(results_dir, "mistakes_evaluation.csv"))

    # Filter relevant columns for plotting
    plot_data = df[['representation_type',
                    'destination_occupied', 'out_of_bounds', 'not_legal_commands',
                    'productive_actions', 'unproductive_actions']].copy()

    # Ensure representation_type is ordered according to representation_types
    if representation_types:
        plot_data['representation_type'] = pd.Categorical(
            plot_data['representation_type'],
            categories=representation_types,
            ordered=True
        )

    # Rename representation_type values
    representation_rename_dict = {
        "text": "Text",
        "vision": "Vision 3D",
        "schematic": "Vision 2D"
    }

    plot_data['representation_type'] = plot_data['representation_type'].astype(str).replace(representation_rename_dict)
    representation_types_renamed = [representation_rename_dict.get(r, r) for r in representation_types]

    plot_data['representation_type'] = pd.Categorical(
        plot_data['representation_type'],
        categories=representation_types_renamed,
        ordered=True
    )

    # Aggregate data per representation type and calculate mean and standard error
    plot_data = plot_data.groupby('representation_type').agg(['mean', 'sem']).reset_index()

    # Flatten multi-index columns
    plot_data.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in plot_data.columns]

    # Melt the data for Seaborn
    melted_data = plot_data.melt(
        id_vars=['representation_type'],
        value_vars=[
            'productive_actions_mean', 'unproductive_actions_mean',
            'destination_occupied_mean', 'out_of_bounds_mean', 'not_legal_commands_mean'
        ],
        var_name='Action',
        value_name='Mean'
    )

    # Add standard error for confidence intervals
    melted_data['CI'] = melted_data['Action'].map(lambda x: plot_data[f"{x.split('_mean')[0]}_sem"].values[0])

    # Create barplot
    plt.figure(figsize=(26, 6))
    ax = sns.barplot(
        data=melted_data,
        x='representation_type',
        y='Mean',
        hue='Action',
        palette=palette,
        ci=None
    )

    # Add error bars for 95% CI
    for bar, (_, row) in zip(ax.patches, melted_data.iterrows()):
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        ax.errorbar(
            x=x,
            y=y,
            yerr=row['CI'] * 1.96,  # 95% CI
            fmt='none',
            color='black',
            capsize=5
        )

    # Add labels on top of each bar
    for bar in ax.patches:
        bar_height = bar.get_height()  # Get bar height
        if not np.isnan(bar_height) and bar_height > 0.0:  # Only add labels for valid and non-zero bars
            bar_x = bar.get_x() + bar.get_width() / 2
            ax.annotate(
                f'{bar_height:.2f}',  # Format the number
                (bar_x, bar_height + label_offset),  # Position slightly above the bar
                ha='center', va='bottom', fontsize=text_size - 4, color='black'
            )

    # Legend renaming
    legend_rename_dict = {
        "productive_actions_mean": "Effective Moves",
        "unproductive_actions_mean": "Ineffective Moves",
        "destination_occupied_mean": "Occupied Destination Moves",
        "out_of_bounds_mean": "Out of Bounds Moves",
        "not_legal_commands_mean": "Illegal Commands",
    }

    handles, labels = ax.get_legend_handles_labels()
    labels = [legend_rename_dict.get(label, label) for label in labels]

    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(labels),
        frameon=False,
        fontsize=text_size-2
    )

    # Set axis labels and title
    ax.set_xlabel("", fontsize=text_size)
    ax.set_ylabel("Average Steps per Episode", fontsize=text_size)

    # Customize ticks
    ax.tick_params(axis='x', rotation=0, labelsize=text_size - 2)
    ax.tick_params(axis='y', labelsize=text_size - 2)

    # Save the plot
    plot_path = os.path.join(plots_dir, "average_barplot_action_counts_with_ci.png")
    plt.tight_layout()
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()
    print(f"Average plot with CI saved at {plot_path}")



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'InternVL', 'llavaonevision-72B', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']
    representation_types = ['vision', 'schematic', 'text']  # Specify the representation types

    # Evaluate and plot for each episode of the experiment
    plot_cumulative_bar_plot_per_modality_with_ci(experiment_id=experiment_id, representation_types=representation_types,)
