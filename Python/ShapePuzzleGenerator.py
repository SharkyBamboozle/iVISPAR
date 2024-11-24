import os
import json
import random
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
import warnings

class ShapePuzzleGenerator:
    bodies = ['cube', 'sphere', 'pyramid','cylinder','cone','prism']
    colors = ['red', 'green', 'blue','yellow','purple','orange']
    labels = ['none', 'cell', 'edge', 'both']

    def __init__(self , board_size=3, num_landmarks=3, instruction_prompt="",experiment_type = 'Puzzle', grid_label= 'none',camera_offset = [0.0,0.0,0.0], screenshot_alpha=1.0):
        # Ensure board_size is the maximum of either 2 or the size required to fit all landmarks
        self.board_size = max(board_size, int((num_landmarks + 1) ** 0.5) + 1, 2)
        self.experiment_type = experiment_type
        self.grid_label = grid_label
        self.camera_offset = camera_offset
        self.screenshot_alpha = screenshot_alpha
        if self.board_size != board_size:
            warnings.warn(f"Board size adjusted to {self.board_size} to fit {num_landmarks} landmarks.")

        # Number of landmarks can be within 1-9
        if num_landmarks < 1 or num_landmarks > 9:
            warnings.warn(f"Number of landmarks out of range, setting to {max(1, min(num_landmarks, 9))}.")
        self.num_landmarks = max(1, min(num_landmarks, 9))

        self.config_id = datetime.now().strftime("%Y%m%d_%H%M%S")  # Setup ID directly assigned here

        self.instruction_prompt = instruction_prompt

        # Set up directory
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.config_root_dir = os.path.join(base_dir, 'configs')
        os.makedirs(self.config_root_dir, exist_ok=True)

    def _generate_unique_landmarks(self):
        """
        Generate unique landmarks with body, color, start, and goal coordinate properties.
        Each landmark must have a unique combination of shape (body) and color,
        and both start and goal coordinates must be unique.
        """

        def generate_coordinate(used_coords):
            """Generate a unique random coordinate not in the used_coords set."""
            while True:
                x = random.randint(0, self.board_size - 1)
                y = random.randint(0, self.board_size - 1)
                coordinate = (x, y)
                if coordinate not in used_coords:
                    return coordinate

        # Sets to store used combinations and coordinates
        used_combinations = set()
        used_start_coordinates = set()
        used_goal_coordinates = set()

        # Generate landmarks
        landmarks = []
        while len(landmarks) < self.num_landmarks:
            body = random.choice(self.bodies)
            color = random.choice(self.colors)
            combination = (body, color)

            # Ensure the combination of body and color is unique
            if combination in used_combinations:
                continue

            # Generate unique start and goal coordinates
            start_coordinate = generate_coordinate(used_start_coordinates)
            goal_coordinate = generate_coordinate(used_goal_coordinates)

            # Add the new landmark if all checks pass
            new_landmark = {
                'body': body,
                'color': color,
                'start_coordinate': start_coordinate,
                'goal_coordinate': goal_coordinate,
            }

            # Track the used combinations and coordinates
            used_combinations.add(combination)
            used_start_coordinates.add(start_coordinate)
            used_goal_coordinates.add(goal_coordinate)

            landmarks.append(new_landmark)

        return landmarks

    def _visualize_landmarks(self, landmarks, filename, coordinate_type='start'):
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

    def generate_configs(self, num_configs):
        """Generate ShapePuzzle configurations and save them to a unique directory."""

        config_dir = os.path.join(self.config_root_dir, f"ShapePuzzle_ID_{self.config_id}")  # Using instance config_id
        os.makedirs(config_dir, exist_ok=True)

        for i in range(num_configs):
            # Generate unique landmarks for this configuration
            landmarks = self._generate_unique_landmarks()

            config_instance_id = f"ShapePuzzle_config_ID_{self.config_id}_{i + 1}"

            # Structure the output for JSON
            json_output = {
                "config_instance_id": config_instance_id,
                "experiment_type": self.experiment_type,
                "instruction_prompt": self.instruction_prompt,
                "grid_size": self.board_size,  # Assuming grid size is fixed and provided by the instance
                "grid_label": self.grid_label,
                "camera_offset": self.camera_offset,
                "screenshot_alpha": self.screenshot_alpha,
                "landmarks": landmarks  # The landmarks list generated
            }

            # Save the configuration to a JSON file
            json_filename = os.path.join(config_dir, f"{config_instance_id}.json")
            with open(json_filename, 'w') as json_file:
                json.dump(json_output, json_file, indent=4)

            # Save the plot of start coordinates
            plot_filename_start = os.path.join(config_dir, f"{config_instance_id}_start.png")
            self._visualize_landmarks(landmarks, plot_filename_start, coordinate_type='start')

            # Save the plot of goal coordinates
            plot_filename_goal = os.path.join(config_dir, f"{config_instance_id}_goal.png")
            self._visualize_landmarks(landmarks, plot_filename_goal, coordinate_type='goal')

        print(f"ShapePuzzle configs generated to {config_dir}")
        return json_output , config_dir


if __name__ == "__main__":
    generator = ShapePuzzleGenerator(board_size=3, num_landmarks=3, instruction_prompt="")
    generator.generate_configs(num_configs=5)
