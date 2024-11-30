# Import statements
import os
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


def visualise_config_stats(config_id):
    """
    Generate a stacked bar plot based on complexity_c1 and complexity_c2
    from JSON configuration files in the given directory.

    Parameters:
        config_id (str): The configuration ID used to locate the JSON directory.
    """

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

    # Apply Seaborn style
    sns.set_theme(style="darkgrid")

    # Data structure to store sums for each complexity_c1
    data = defaultdict(lambda: defaultdict(int))  # {complexity_c1: {complexity_c2: count}}

    # Iterate through files in the directory
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, 'r') as file:
                try:
                    config = json.load(file)
                    c1 = config.get("complexity_c1", None)  # Adjusted key
                    c2 = config.get("complexity_c2", None)  # Adjusted key
                    if c1 is not None and c2 is not None:
                        data[c1][c2] += 1
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping.")

    # Prepare data for plotting
    sorted_data = dict(sorted(data.items()))  # Sort by complexity_c1
    complexity_c1 = list(sorted_data.keys())

    # Create a list of unique complexity_c2 values for consistent coloring
    all_c2_values = sorted({c2 for c1_data in sorted_data.values() for c2 in c1_data})
    bar_segments = {c2: [] for c2 in all_c2_values}  # To store segment heights

    for c1 in complexity_c1:
        for c2 in all_c2_values:
            bar_segments[c2].append(sorted_data[c1].get(c2, 0))  # Append 0 if no such c2 for this c1

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    bottom_values = [0] * len(complexity_c1)  # Track cumulative height for stacking

    # Use a modern color palette
    colors = sns.color_palette("pastel", len(all_c2_values))

    for i, c2 in enumerate(all_c2_values):
        ax.bar(
            complexity_c1,
            bar_segments[c2],
            bottom=bottom_values,
            label=f'complexity_c2: {c2}',
            color=colors[i % len(colors)]
        )
        # Update bottom values for stacking
        bottom_values = [b + h for b, h in zip(bottom_values, bar_segments[c2])]

    # Add labels, title, and legend
    ax.set_xlabel('Complexity C1', fontsize=14)
    ax.set_ylabel('Total Complexity C2', fontsize=14)
    ax.set_title('Stacked Bar Plot of Complexity C1', fontsize=16)
    ax.legend(title="Segments by complexity_c2", loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.8)

    # Save and display the plot
    plt.tight_layout()
    filename = os.path.join(config_dir, "complexity_distribution.png")
    plt.savefig(filename)
    plt.show()


if __name__ == "__main__":
    visualise_config_stats(config_id="SGP_ID_20241129_002252")