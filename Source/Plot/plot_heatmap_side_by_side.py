import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="darkgrid")

def plot_heat_map_episode_level_average(
    experiment_id, compiled_csv="episode_outcomes_evaluation.csv",
    model_types=None, representation_types=None, text_size=18):


    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    heatmap_dir = os.path.join(results_dir, 'heatmaps_average')  # Subdirectory for averaged heatmaps
    os.makedirs(heatmap_dir, exist_ok=True)

    compiled_path = os.path.join(results_dir, compiled_csv)
    eval_df = pd.read_csv(compiled_path)

    required_columns = ['episode_nr', 'model_type', 'representation_type', 'min_path_length', 'spl_value',
                        'won', 'won_at_spl', 'num_geoms', 'complexity_c1']
    if not all(col in eval_df.columns for col in required_columns):
        raise ValueError("The compiled CSV is missing required columns.")

    if model_types:
        eval_df = eval_df[eval_df['model_type'].isin(model_types)]

    if representation_types:
        eval_df = eval_df[eval_df['representation_type'].isin(representation_types)]

    if eval_df.empty:
        print("No data found for the specified model types or representation types.")
        return

    # Rename representation_type values
    representation_rename_dict = {
        "text": "Text",
        "vision": "Vision 3D",
        "schematic": "Vision 2D"
    }

    eval_df['representation_type'] = eval_df['representation_type'].replace(representation_rename_dict)
    representation_types_renamed = [representation_rename_dict.get(r, r) for r in representation_types]

    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']
    geom_range = sorted(eval_df['num_geoms'].unique())
    c1_range = sorted(eval_df['complexity_c1'].unique())

    for metric in metrics:
        vmin = eval_df[metric].min()
        vmax = eval_df[metric].max()

        # Manually set vmax for specific metrics
        if metric == 'min_path_length':
            vmax = 10.0  # Example: Set the maximum value for 'min_path_length'
        elif metric == 'spl_value':
            vmax = 12.0  # Example: Set the maximum value for 'spl_value'
        elif metric == 'won':
            pass

        fig_width_per_heatmap = 8  # Increased width per heatmap
        fig_height = 8  # Increased height for square heatmaps
        total_width = len(representation_types_renamed) * fig_width_per_heatmap
        fig, axes = plt.subplots(
            1, len(representation_types_renamed),
            figsize=(total_width, fig_height),
            sharey=True
        )

        cbar_ax = fig.add_axes([0.92, 0.15, 0.03, 0.7])  # Adjust colorbar position

        for i, rep_type in enumerate(representation_types_renamed):
            heatmap_data = (
                eval_df[eval_df["representation_type"] == rep_type]
                .groupby(["num_geoms", "complexity_c1"])[metric]
                .mean()
                .unstack(level=0)
                .reindex(index=c1_range, columns=geom_range, fill_value=0)
            )
            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt=".2f",
                cmap="viridis_r",
                cbar=(i == len(representation_types_renamed) - 1),
                ax=axes[i],
                square=True,
                vmin=vmin,
                vmax=vmax,
                cbar_ax=cbar_ax if i == len(representation_types_renamed) - 1 else None,
                annot_kws={"size": text_size - 4}  # Annotation font size
            )
            axes[i].invert_yaxis()
            axes[i].set_title(f"{rep_type}", fontsize=text_size+2)
            axes[i].set_xlabel("Number of Geoms", fontsize=text_size+2)
            if i == 0:
                axes[i].set_ylabel("Shortest Path Solution", fontsize=text_size+2)
            else:
                axes[i].set_ylabel("")
            axes[i].tick_params(axis="both", which="major", labelsize=text_size - 2)

        # Adjust colorbar tick labels
        cbar_ax.tick_params(labelsize=text_size - 2)

        fig.subplots_adjust(right=0.9, wspace=0.1)  # Reduce wspace to decrease space between plots

        model_part = '_'.join(model_types) if model_types else 'All'
        representation_part = '_'.join(representation_types_renamed) if representation_types_renamed else 'All'
        plot_path = os.path.join(heatmap_dir, f'heatmap_avg_{metric}_{model_part}_{representation_part}_shared_scale.png')
        plt.savefig(plot_path, bbox_inches='tight')
        plt.close()
        print(f"Averaged {metric.replace('_', ' ').capitalize()} heatmaps saved at {plot_path}")




if __name__ == "__main__":
    experiment_id = 'ICML_all'
    representation_types = ['vision', 'schematic', 'text']  # Specify the representation types
    model_types =  ['claude-3-5-sonnet-20241022', 'gemini-2.0-flash-exp', 'gpt-4o', 'llavaonevision-72B', 'InternVL', 'Qwen2-VL-72B-Instruct-GPTQ-Int4']
    model_types = ['Qwen2-VL-72B-Instruct']

    plot_heat_map_episode_level_average(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=representation_types
    )
