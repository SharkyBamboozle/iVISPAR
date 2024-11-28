import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import os
import json
import re
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns

def visualize_config_stats(config_dir):
    """
    Generate a stacked bar plot based on complexity_first_order and complexity_second_order
    from JSON configuration files in the given directory.

    Parameters:
        config_dir (str): Path to the directory containing JSON configuration files.
    """
    # Apply Seaborn style
    sns.set_theme(style="darkgrid")

    # Data structure to store sums for each complexity_first_order
    data = defaultdict(lambda: defaultdict(int))  # {complexity_first_order: {complexity_second_order: count}}

    # Iterate through files in the directory
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, 'r') as file:
                try:
                    config = json.load(file)
                    c1 = config.get("complexity_first_order", None)
                    c2 = config.get("complexity_second_order", None)
                    if c1 is not None and c2 is not None:
                        data[c1][c2] += 1
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping.")

    # Prepare data for plotting
    sorted_data = dict(sorted(data.items()))  # Sort by complexity_first_order
    complexity_first_order = list(sorted_data.keys())

    # Create a list of unique complexity_second_order values for consistent coloring
    all_c2_values = sorted({c2 for c1_data in sorted_data.values() for c2 in c1_data})
    bar_segments = {c2: [] for c2 in all_c2_values}  # To store segment heights

    for c1 in complexity_first_order:
        for c2 in all_c2_values:
            bar_segments[c2].append(sorted_data[c1].get(c2, 0))  # Append 0 if no such c2 for this c1

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    bottom_values = [0] * len(complexity_first_order)  # Track cumulative height for stacking

    # Use a modern color palette
    colors = sns.color_palette("pastel", len(all_c2_values))

    for i, c2 in enumerate(all_c2_values):
        ax.bar(
            complexity_first_order,
            bar_segments[c2],
            bottom=bottom_values,
            label=f'complexity_second_order: {c2}',
            color=colors[i % len(colors)]
        )
        # Update bottom values for stacking
        bottom_values = [b + h for b, h in zip(bottom_values, bar_segments[c2])]

    # Add labels, title, and legend
    ax.set_xlabel('Complexity First Order', fontsize=14)
    ax.set_ylabel('Total Complexity Second Order', fontsize=14)
    ax.set_title('Stacked Bar Plot of Complexity First Order', fontsize=16)
    ax.legend(title="Segments by complexity_second_order", loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.8)

    # Save and display the plot
    plt.tight_layout()
    filename = os.path.join(config_dir, "complexity_distribution.png")
    plt.savefig(filename)
    #plt.show()



def visualize_config_stats_2(config_dir):
    """
    Generate a stacked bar plot based on complexity_first_order and complexity_second_order
    from JSON configuration files in the given directory.

    Parameters:
        config_dir (str): Path to the directory containing JSON configuration files.
    """
    # Data structure to store sums for each complexity_first_order
    data = defaultdict(lambda: defaultdict(int))  # {complexity_first_order: {complexity_second_order: count}}

    # Iterate through files in the directory
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(config_dir, filename)
            with open(filepath, 'r') as file:
                try:
                    config = json.load(file)
                    c1 = config.get("complexity_first_order", None)
                    c2 = config.get("complexity_second_order", None)
                    if c1 is not None and c2 is not None:
                        data[c1][c2] += 1
                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping.")

    # Prepare data for plotting
    sorted_data = dict(sorted(data.items()))  # Sort by complexity_first_order
    complexity_first_order = list(sorted_data.keys())

    # Create a list of unique complexity_second_order values for consistent coloring
    all_c2_values = sorted({c2 for c1_data in sorted_data.values() for c2 in c1_data})
    bar_segments = {c2: [] for c2 in all_c2_values}  # To store segment heights

    for c1 in complexity_first_order:
        for c2 in all_c2_values:
            bar_segments[c2].append(sorted_data[c1].get(c2, 0))  # Append 0 if no such c2 for this c1

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    bottom_values = [0] * len(complexity_first_order)  # Track cumulative height for stacking

    colors = plt.cm.tab20.colors  # Use a colormap for unique colors
    for i, c2 in enumerate(all_c2_values):
        ax.bar(
            complexity_first_order,
            bar_segments[c2],
            bottom=bottom_values,
            label=f'complexity_second_order: {c2}',
            color=colors[i % len(colors)]
        )
        # Update bottom values for stacking
        bottom_values = [b + h for b, h in zip(bottom_values, bar_segments[c2])]

    # Add labels, title, and legend
    ax.set_xlabel('Complexity First Order', fontsize=12)
    ax.set_ylabel('Total Complexity Second Order', fontsize=12)
    ax.set_title('Stacked Bar Plot of Complexity First Order', fontsize=14)
    ax.legend(title="Segments by complexity_second_order", loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Save and display the plot
    plt.tight_layout()
    filename = os.path.join(config_dir, "complexity_distribution.png")
    plt.savefig(filename)
    plt.show()

def visualize_config_stats_3(config_dir):
    # Dictionary to store the highest "i" value for each "c" value
    c_values = {}

    # Regular expression to match the file naming convention
    pattern = re.compile(r"SGP_config_ID_\d+_\d+_c_(\d+)_i_(\d+)\.json")

    # Iterate through files in the directory
    for filename in os.listdir(config_dir):
        if filename.endswith('.json'):
            match = pattern.match(filename)
            if match:
                c_value = int(match.group(1))  # Extract the c value
                i_value = int(match.group(2))  # Extract the i value

                # Update the dictionary with the highest i value for each c value
                if c_value not in c_values or i_value > c_values[c_value]:
                    c_values[c_value] = i_value

    # Sort the c_values dictionary by key (c value)
    sorted_c_values = dict(sorted(c_values.items()))

    # Generate the barplot
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_c_values.keys(), sorted_c_values.values())
    plt.xlabel('c Values')
    plt.ylabel('Highest i Value')
    plt.title('Barplot of Highest i Values for Each c Value')
    plt.xticks(list(sorted_c_values.keys()))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Show the plot
    plt.show()
    filename = os.path.join(config_dir, f"complexity_distribution.png")
    plt.savefig(filename)


def visualize_configs(config_dir):
    pass
def visualize_shortest_sequence(config_dir):
    pass


# generate image with initial and goal state
def visualize_landmarks(self, landmarks, filename, coordinate_type='start'):
    """
    Visualize the grid with landmarks using matplotlib.

    Args:
        landmarks (list): List of landmarks with their properties.
        filename (str): Path to save the visualized plot.
        coordinate_type (str): Type of coordinate to visualize ('start' or 'goal').
                               Default is 'start'.
    """
    fig, ax = plt.subplots(figsize=(self.board_size, self.board_size))

    # Create the grid
    for x in range(self.board_size):
        for y in range(self.board_size):
            ax.add_patch(Rectangle((x, y), 1, 1, edgecolor='black', facecolor='white'))

    # Visualize landmarks based on the coordinate type ('start' or 'goal')
    for landmark in landmarks:
        # Use 'start_coordinate' or 'goal_coordinate' based on the coordinate_type argument
        coordinate = landmark.get(f'{coordinate_type}_coordinate', None)

        # Skip if the coordinate does not exist
        if coordinate is None:
            continue

        x, y = coordinate
        color = landmark['color']

        # Draw the landmark based on its body type
        if landmark['body'] == 'cube':
            ax.add_patch(Rectangle((x, y), 1, 1, color=color, alpha=0.6))
        elif landmark['body'] == 'sphere':
            ax.add_patch(Circle((x + 0.5, y + 0.5), 0.5, color=color, alpha=0.6))
        elif landmark['body'] == 'pyramid':
            ax.add_patch(Polygon([[x + 0.5, y + 1], [x, y], [x + 1, y]], color=color, alpha=0.6))

    ax.set_xlim(0, self.board_size)
    ax.set_ylim(0, self.board_size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')

    # Save the plot to a file
    plt.savefig(filename)

if __name__ == "__main__":
    visualize_config_stats(r'C:\Users\Sharky\RIPPLE\Data\Configs\SGP_ID_20241127_121145')