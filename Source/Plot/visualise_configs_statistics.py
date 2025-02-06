# Import statements
import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

def visualise_config_stats(config_id):
    """
    Combine the functionality of visualizing landmark statistics (shapes, colors, combinations)
    and config statistics (complexity_c1 and complexity_c2) into a single 4x1 subplot figure.

    Parameters:
        config_id (str): The configuration ID used to locate the JSON directory.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

    # Initialize counters for shapes, colors, combinations, and complexity bins
    shape_counts = defaultdict(int)
    color_counts = defaultdict(int)
    combination_counts = defaultdict(int)
    complexity_data = defaultdict(lambda: defaultdict(int))  # {complexity_c1: {complexity_c2: count}}

    # Iterate through files in the directory
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, 'r') as file:
                try:
                    config = json.load(file)

                    # Process landmarks for shapes, colors, and combinations
                    landmarks = config.get("landmarks", [])
                    for landmark in landmarks:
                        shape = landmark.get("body", "unknown")
                        color = landmark.get("color", "unknown")
                        combination = f"{color} {shape}"

                        shape_counts[shape] += 1
                        color_counts[color] += 1
                        combination_counts[combination] += 1

                    # Process complexity data
                    c1 = config.get("complexity_c1", None)
                    c2 = config.get("complexity_c2", None)
                    if c1 is not None and c2 is not None:
                        complexity_data[c1][c2] += 1
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping.")

    # Prepare data for complexity stacked bar plot
    sorted_complexity_data = dict(sorted(complexity_data.items()))  # Sort by complexity_c1
    complexity_c1 = list(sorted_complexity_data.keys())
    all_c2_values = sorted({c2 for c1_data in sorted_complexity_data.values() for c2 in c1_data})
    bar_segments = {c2: [] for c2 in all_c2_values}

    for c1 in complexity_c1:
        for c2 in all_c2_values:
            bar_segments[c2].append(sorted_complexity_data[c1].get(c2, 0))

    # Create a 4x1 subplot figure
    sns.set_theme(style="darkgrid")
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), constrained_layout=False)
    fig.subplots_adjust(hspace=0.8)  # Adjust vertical spacing between subplots

    # Complexity Stacked Bar Plot
    bottom_values = [0] * len(complexity_c1)
    colors = sns.color_palette("pastel", len(all_c2_values))
    for i, c2 in enumerate(all_c2_values):
        axes[0].bar(
            complexity_c1,
            bar_segments[c2],
            bottom=bottom_values,
            label=f'c2: {c2}',
            color=colors[i % len(colors)]
        )
        bottom_values = [b + h for b, h in zip(bottom_values, bar_segments[c2])]

    axes[0].set_title("Complexity C1-C2", fontsize=16)
    axes[0].set_xlabel("C1", fontsize=12)
    axes[0].set_ylabel("Count", fontsize=12)
    axes[0].legend(title="C2 Segments", loc="upper right")

    # Combined Shapes and Colors
    combined_keys = list(shape_counts.keys()) + list(color_counts.keys())
    combined_values = list(shape_counts.values()) + list(color_counts.values())
    combined_colors = sns.color_palette("pastel", len(shape_counts)) + sns.color_palette("deep", len(color_counts))

    axes[1].bar(combined_keys, combined_values, color=combined_colors)
    axes[1].set_title("Shapes and Colors", fontsize=16)
    axes[1].set_xlabel("Shapes & Colors", fontsize=12)
    axes[1].set_ylabel("Count", fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)

    # Combinations
    axes[2].bar(combination_counts.keys(), combination_counts.values(), color=sns.color_palette("muted"))
    axes[2].set_title("Color-Shape Combinations", fontsize=16)
    axes[2].set_xlabel("Combination", fontsize=12)
    axes[2].set_ylabel("Count", fontsize=12)
    axes[2].tick_params(axis='x', rotation=45)

    # Save and show the plot
    plt.savefig(os.path.join(config_dir, "config_stats_visualisation.png"))
    plt.show()

    print(f"Combined plot saved in {config_dir}")


if __name__ == "__main__":
    visualise_config_stats(config_id="ICML")
