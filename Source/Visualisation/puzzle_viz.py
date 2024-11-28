import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import matplotlib.colors as mcolors

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by blending it with white.

    Parameters:
        color (str): Base color as a string (e.g., 'red', 'blue') or hex.
        amount (float): Amount to lighten (0 = no change, 1 = fully white).

    Returns:
        str: A lighter version of the color in hex format.
    """
    try:
        c = mcolors.to_rgb(color)
        white = (1, 1, 1)
        new_color = tuple((1 - amount) * c[i] + amount * white[i] for i in range(3))
        return mcolors.to_hex(new_color)
    except ValueError:
        return color  # Return original if color cannot be processed.

def visualize_board_states(bodies, colors):
    """
    Visualizes a list of objects (bodies) on a 2D board using Matplotlib.

    Parameters:
        bodies (list): A list of strings representing object types, e.g.,
                       ['cube', 'sphere', 'pyramid', 'cylinder', 'cone'].
        colors (list): A list of colors corresponding to each object in `bodies`.
    """
    if len(bodies) != len(colors):
        raise ValueError("The length of bodies and colors must match.")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Setting up the board dimensions
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.set_title("Board State Visualization")
    ax.grid(True)

    # Visualizing each object
    for i, (body, color) in enumerate(zip(bodies, colors)):
        x = 1 + 2 * i  # X-coordinate of the object
        y = 5          # Fixed Y-coordinate for simplicity

        if body == 'cube':
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, color=color))
            ax.text(x, y - 0.7, 'Cube', ha='center', va='center', fontsize=8)

        elif body == 'sphere':
            ax.add_patch(Circle((x, y), 0.5, color=color))
            ax.text(x, y - 0.7, 'Sphere', ha='center', va='center', fontsize=8)

        elif body == 'pyramid':
            ax.add_patch(Polygon([[x - 0.5, y - 0.5], [x + 0.5, y - 0.5], [x, y + 0.5]], color=color))
            ax.text(x, y - 0.7, 'Pyramid', ha='center', va='center', fontsize=8)

        elif body == 'cylinder':
            lighter_color = lighten_color(color, amount=0.5)

            # Bottom circle
            ax.add_patch(Circle((x, y - 0.3), 0.5, color=color))
            # Rectangle connecting top and bottom
            ax.add_patch(Rectangle((x - 0.5, y - 0.3), 1, 0.6, color=color))
            # Top circle with lighter hue
            ax.add_patch(Circle((x, y + 0.3), 0.5, color=lighter_color))
            ax.text(x, y - 0.7, 'Cylinder', ha='center', va='center', fontsize=8)

        elif body == 'cone':
            lighter_color = lighten_color(color, amount=0.5)

            # Base circle (larger, darker hue)
            ax.add_patch(Circle((x, y - 0.3), 0.5, color=color))
            # Smaller top circle (centered, lighter hue)
            ax.add_patch(Circle((x, y - 0.3), 0.3, color=lighter_color))
            ax.text(x, y - 0.7, 'Cone', ha='center', va='center', fontsize=8)

    # Show plot
    plt.show()

# Example usage
bodies = ['cube', 'sphere', 'pyramid', 'cylinder', 'cone']
colors = ['red', 'green', 'blue', 'yellow', 'purple']
visualize_board_states(bodies, colors)
