import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_config_state_distribution(config_id):
    """
    Visualize the difference between the percentage of states in each field and the expected percentage for an even distribution.

    Args:
        config_id (str): The identifier for the configuration directory.
    """
    # Set up the directory paths
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

    # Load all config files from the directory
    json_file_paths = [
        os.path.join(config_dir, file_name)
        for file_name in os.listdir(config_dir)
        if file_name.endswith(".json")
    ]

    if not json_file_paths:
        print("No configuration files found in the directory.")
        return

    # Initialize variables to store the counts
    start_state_counts = None
    goal_state_counts = None

    # Process each JSON file
    total_states = 0
    for json_file_path in json_file_paths:
        with open(json_file_path, 'r') as file:
            config = json.load(file)

        grid_size = config['grid_size']

        # Initialize heatmaps if not already initialized
        if start_state_counts is None or goal_state_counts is None:
            start_state_counts = np.zeros((grid_size, grid_size))
            goal_state_counts = np.zeros((grid_size, grid_size))

        for landmark in config['landmarks']:
            start_coord = landmark['start_coordinate']
            goal_coord = landmark['goal_coordinate']

            # Increment the respective heatmap cells
            start_state_counts[start_coord[0], start_coord[1]] += 1
            goal_state_counts[goal_coord[0], goal_coord[1]] += 1
            total_states += 1

    # Calculate the expected percentage for an even distribution
    grid_size = start_state_counts.shape[0]
    total_cells = grid_size ** 2
    expected_percentage = 100 / total_cells

    # Calculate the percentage difference heatmaps
    start_percentage_diff = (start_state_counts / total_states * 100) - expected_percentage
    goal_percentage_diff = (goal_state_counts / total_states * 100) - expected_percentage

    # Determine the shared range for the heatmap color bar
    max_diff = max(np.max(start_percentage_diff), np.max(goal_percentage_diff))
    min_diff = min(np.min(start_percentage_diff), np.min(goal_percentage_diff))

    # Create a side-by-side plot with a shared color bar
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 1.05]})

    # Plot Initial State Percentage Difference
    sns.heatmap(
        start_percentage_diff,
        annot=True,
        fmt=".2f",
        cmap="RdBu",
        cbar=False,
        square=True,
        center=0,
        vmin=min_diff,
        vmax=max_diff,
        ax=axes[0]
    )
    axes[0].invert_yaxis()  # Invert y-axis for bottom-left origin
    axes[0].set_title("Initial State Percentage Difference")
    axes[0].set_xlabel("X Coordinate")
    axes[0].set_ylabel("Y Coordinate")

    # Plot Goal State Percentage Difference
    sns.heatmap(
        goal_percentage_diff,
        annot=True,
        fmt=".2f",
        cmap="RdBu",
        cbar=True,
        square=True,
        center=0,
        vmin=min_diff,
        vmax=max_diff,
        ax=axes[1],
        cbar_kws={"label": "Percentage Difference (%)"}
    )
    axes[1].invert_yaxis()  # Invert y-axis for bottom-left origin
    axes[1].set_title("Goal State Percentage Difference")
    axes[1].set_xlabel("X Coordinate")
    axes[1].set_ylabel("Y Coordinate")

    # Add a header showing the number of samples
    total_samples = len(json_file_paths)
    fig.suptitle(f"State Distribution Heatmaps (Based on {total_samples} Configurations)", fontsize=16, y=0.98)

    # Adjust layout to avoid truncation
    plt.subplots_adjust(top=0.85)

    # Save the combined plot
    plot_path = os.path.join(config_dir, "state_distribution_shared_heatmaps.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.show()
    plt.close()
    print(f"State distribution heatmaps saved at {plot_path}")

if __name__ == "__main__":
    config_id = "ICML"  # Replace with your actual config_id
    visualize_config_state_distribution(config_id=config_id)
