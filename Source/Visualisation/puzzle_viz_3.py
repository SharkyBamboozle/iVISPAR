import os
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon


def visualize_landmarks(ax, landmarks, coordinate_type, board_size=5):
    """
    Visualizes the grid with landmarks on a given Matplotlib axis.

    Args:
        ax (matplotlib.axes.Axes): The axis to draw on.
        landmarks (list): List of landmarks with their properties.
        coordinate_type (str): Type of coordinate to visualize ('start' or 'goal').
        board_size (int): Size of the board (default: 5).
    """
    # Create the grid
    for x in range(board_size):
        for y in range(board_size):
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
        elif landmark['body'] == 'cylinder':
            ax.add_patch(Circle((x + 0.5, y + 0.7), 0.3, color=color, alpha=0.6))
            ax.add_patch(Circle((x + 0.5, y + 0.3), 0.3, color=color, alpha=0.3))

    ax.set_xlim(0, board_size)
    ax.set_ylim(0, board_size)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.set_title(f'{coordinate_type.capitalize()} State')


def process_json_files(dir_path, board_size=5):
    """
    Crawls through JSON files in a directory, visualizes the start and goal states,
    and saves the visualizations as images.

    Args:
        dir_path (str): Path to the directory containing JSON files.
        board_size (int): Size of the board (default: 5).
    """
    for filename in os.listdir(dir_path):
        if filename.endswith('.json'):
            filepath = os.path.join(dir_path, filename)
            with open(filepath, 'r') as file:
                try:
                    data = json.load(file)
                    landmarks = data.get('landmarks', [])

                    # Create side-by-side plots
                    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

                    # Plot start state
                    visualize_landmarks(axes[0], landmarks, 'start', board_size)

                    # Plot goal state
                    visualize_landmarks(axes[1], landmarks, 'goal', board_size)

                    # Save the figure
                    plt.show()
                    output_path = os.path.join(dir_path, f"{os.path.splitext(filename)[0]}.png")
                    plt.tight_layout()
                    plt.savefig(output_path)
                    plt.close(fig)

                except json.JSONDecodeError:
                    print(f"Error decoding {filename}, skipping.")


# Example usage:
process_json_files(r'C:\Users\Sharky\RIPPLE\Data\Configs\SGP_ID_20241127_121145')
