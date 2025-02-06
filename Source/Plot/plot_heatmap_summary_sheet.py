import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="darkgrid")

def plot_combined_heatmaps_with_titles(
    experiment_id, compiled_csv="episode_outcomes_evaluation.csv",
    model_types=None, representation_types=None
):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    heatmap_dir = os.path.join(results_dir, 'heatmaps_combined')  # Subdirectory for combined heatmaps
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

    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']
    geom_range = sorted(eval_df['num_geoms'].unique())
    c1_range = sorted(eval_df['complexity_c1'].unique())

    fig, axes = plt.subplots(
        nrows=len(metrics), ncols=len(representation_types),
        figsize=(24, 48), sharey=True
    )

    fig.subplots_adjust(hspace=0.5, wspace=0.1)

    for row_idx, metric in enumerate(metrics):
        vmin = eval_df[metric].min()
        vmax = eval_df[metric].max()

        for col_idx, rep_type in enumerate(representation_types):
            heatmap_data = (
                eval_df[eval_df["representation_type"] == rep_type]
                .groupby(["num_geoms", "complexity_c1"])[metric]
                .mean()
                .unstack(level=0)
                .reindex(index=c1_range, columns=geom_range, fill_value=0)
            )

            cbar_ax = fig.add_axes([0.92, 0.8 - row_idx * 0.2, 0.02, 0.15]) if col_idx == len(representation_types) - 1 else None

            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt=".2f",
                cmap="viridis_r",
                cbar=(col_idx == len(representation_types) - 1),
                ax=axes[row_idx, col_idx],
                square=True,
                vmin=vmin,
                vmax=vmax,
                cbar_ax=cbar_ax
            )

            axes[row_idx, col_idx].invert_yaxis()
            axes[row_idx, col_idx].set_xlabel("Number of Geoms")

            if col_idx == 0:
                axes[row_idx, col_idx].set_ylabel("Shortest Path Solution")

            if row_idx == 0:
                axes[row_idx, col_idx].set_title(f"{rep_type.capitalize()}", fontsize=14)

        # Add a row-level title
        fig.text(0.5, 0.81 - row_idx * 0.2, f"Averaged {metric.replace('_', ' ').capitalize()} Heatmaps",
                 fontsize=16, ha="center", weight="bold")

    model_part = '_'.join(model_types) if model_types else 'All'
    representation_part = '_'.join(representation_types) if representation_types else 'All'
    plot_path = os.path.join(heatmap_dir, f'combined_heatmaps_{model_part}_{representation_part}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()
    print(f"Combined heatmaps saved at {plot_path}")


if __name__ == "__main__":
    experiment_id = 'ICML_all'
    modalities = ['text', 'vision']  # Specify the representation types
    model_types = ['claude-3-5-sonnet-20241022']

    plot_combined_heatmaps_with_titles(
        experiment_id=experiment_id,
        model_types=model_types,
        representation_types=modalities
    )
