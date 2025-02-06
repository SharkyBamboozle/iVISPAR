import os
import pandas as pd
import seaborn as sns

# Set the Seaborn style
sns.set_style('darkgrid')

palette = ["#13315c", "#3d5a80", "#98c1d9", "#ee6c4d", "#ff4800"]
palette1 = ["#fb8500", "#ffb703", "#1d3557", "#457b9d", "#2a9d8f"]



def plot_bar_plot_with_ci(experiment_id, model_types=None, representation_types=None, text_size=45):
    # Set result directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    plots_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id, 'mistakes')
    os.makedirs(plots_dir, exist_ok=True)

    # Load data
    df = pd.read_csv(os.path.join(results_dir, "mistakes_evaluation.csv"))

    # Filter relevant columns for plotting
    plot_data = df[['model_type', 'representation_type',
                    'destination_occupied', 'out_of_bounds', 'not_legal_commands',
                    'productive_actions', 'unproductive_actions']].copy()

    # Ensure model_type is ordered according to model_types
    if model_types:
        plot_data.loc[:, 'model_type'] = pd.Categorical(
            plot_data['model_type'],
            categories=model_types,
            ordered=True
        )

    # Ensure representation_type is ordered according to representation_types
    if representation_types:
        plot_data.loc[:, 'representation_type'] = pd.Categorical(
            plot_data['representation_type'],
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

    plot_data['model_type'] = plot_data['model_type'].astype(str).replace(model_rename_dict)
    model_types_renamed = [model_rename_dict.get(m, m) for m in model_types]

    plot_data['model_type'] = pd.Categorical(
        plot_data['model_type'],
        categories=model_types_renamed,
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

    # Melt the data for Seaborn
    plot_data = plot_data.melt(
        id_vars=['model_type', 'representation_type'],
        value_vars=['productive_actions', 'unproductive_actions', 'destination_occupied', 'out_of_bounds', 'not_legal_commands'],
        var_name='Action',
        value_name='Count'
    )

    # Create FacetGrid
    g = sns.FacetGrid(
        plot_data,
        col="representation_type",
        col_order=representation_types_renamed,
        height=16,
        aspect=1.5,
        sharey=True
    )

    # Map barplot
    g.map_dataframe(
        sns.barplot,
        x="model_type",
        y="Count",
        hue="Action",
        dodge=True,
        order=model_types_renamed,
        palette=palette,
        capsize=0.1,
        errorbar="ci"
    )

    # Legend renaming
    legend_rename_dict = {
        "productive_actions": "Effective Moves",
        "unproductive_actions": "Ineffective Moves",
        "destination_occupied": "Occupied Destination Moves",
        "out_of_bounds": "Out of Bounds Moves",
        "not_legal_commands": "Illegal Commands",
    }

    for ax in g.axes.flat:
        handles, labels = ax.get_legend_handles_labels()
        break

    labels = [legend_rename_dict.get(label, label) for label in labels]

    g.fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(labels),
        frameon=False,
        fontsize=text_size-2
    )

    for ax in g.axes.flat:
        if ax.legend_ is not None:
            ax.legend_.remove()

    g.set_titles("{col_name}", size=text_size)  # Set size of representation type labels
    g.tick_params(axis='y', labelsize=text_size-2)  # Increase y-axis tick label size to 14 (or desired size)
    g.set_axis_labels("", "Average Steps per Episode", fontsize=text_size+2)
    g.set_xticklabels(rotation=45, ha="right", fontsize=text_size-2)

    plot_path = os.path.join(plots_dir, "barplot_action_counts_with_error_bars_per_model_and_representation.png")
    g.savefig(plot_path, bbox_inches="tight")
    print(f"Plot saved at {plot_path}")



if __name__ == "__main__":

    experiment_id = 'ICML_all'
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'InternVL', 'llavaonevision-72B', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']
    representation_types = ['vision', 'schematic', 'text']  # Specify the representation types
    #model_types = ['Qwen2-VL-72B-Instruct']

    # Evaluate and plot for each episode of the experiment
    plot_bar_plot_with_ci(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=representation_types,
    )
