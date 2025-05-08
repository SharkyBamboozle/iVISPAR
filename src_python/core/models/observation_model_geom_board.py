import io
import os
import logging
import base64
import json
from PIL import Image, ImageDraw, ImageFont

from .observation_model import ObservationModel
from ..utility.json_file_handler import JsonFileHandler


import io
import numpy as np

from PIL import Image, ImageDraw, ImageFont

import matplotlib
matplotlib.use("Agg")

import matplotlib.colors as mcolors
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import seaborn as sns


@ObservationModel.register_subclass("geom_board")
class ObservationModelGeomBoard(ObservationModel):
    def __init__(self, state_data: dict, goal_data: dict, game_params: dict = None):

        super().__init__(state_data, goal_data, game_params)

        self.instructions = JsonFileHandler.load_json(file_signature=game_params['instructions'],source_dir='instructions')
        self.state_board_data = state_data['messages']
        self.goal_board_data = goal_data['messages']
        self.state_image = StateImageRepresentation(state_data)
        self.goal_image = StateImageRepresentation(goal_data)


    @property
    def board_data(self) -> bool:
        return self.state_board_data[0]['board_data']

    @property
    def is_done(self) -> bool:
        return self.state_board_data[0]['game_done']

    @property
    def action(self) -> str:
        return self.state_board_data[0]['Actions']

    @property
    def validity(self) -> str:
        return self.state_board_data.get("validity", "NoneValidity")

    @property
    def step_num(self) -> int:
        return self.state_board_data[0]['step_num']

    @property
    def system_prompt(self) -> str:
        return self.instructions['system_prompt']

    @property
    def chain_of_thoughts(self) -> str:
        return self.instructions['chain_of_thoughts']

    @property
    def no_chain_of_thoughts(self) -> str:
        return self.instructions['no_chain_of_thoughts']

    @property
    def task_description(self) -> str:
        return self.instructions['task_description']

    #-------------------------------#
    #           Modalities          #
    #-------------------------------#
    @property
    def state_representation(self):
        if self.game_params['representation_type'] == 'vision':
            return self.state_image.image_3d_base64_labeled
        elif self.game_params['representation_type'] == 'text':
            return self.state_board_data[0]['board_state']
        elif self.game_params['representation_type'] == 'schematic':
            return self.state_image.image_2d_base64_labeled

    @property
    def goal_representation(self):
        if self.game_params['representation_type'] == 'vision':
            return self.goal_image.image_3d_base64_labeled
        elif self.game_params['representation_type'] == 'text':
            return self.goal_board_data[0]['board_state']
        elif self.game_params['representation_type'] == 'schematic':
            return self.goal_image.image_2d_base64_labeled


class StateImageRepresentation:
    def __init__(self, message_data):

        self.color_codes = JsonFileHandler.load_json(file_signature='color_codes', source_dir='settings')

        self.image_base64_original = message_data.get("payload", [""])

        self.image_object_3d = self.image_from_base64(self.image_base64_original)
        self.image_object_3d_color_coded = self.color_code_observation(self.image_object_3d.copy(), tuple(self.color_codes['active_1']['rgb']))
        self.image_object_3d_color_coded_label = self.add_action_text(self.image_object_3d_color_coded.copy(), 'active')
        self.image_3d_base64_labeled = self.encode_image_from_pil(self.image_object_3d_color_coded_label)

        self.image_object_2d = self.schematic_from_data(message_data.get("state_board_data", []))
        self.image_object_2d_color_coded = self.color_code_observation(self.image_object_2d.copy(), tuple(self.color_codes['active_1']['rgb']))
        self.image_object_2d_color_coded_label = self.add_action_text(self.image_object_2d_color_coded.copy(), 'active')
        self.image_2d_base64_labeled = self.encode_image_from_pil(self.image_object_2d_color_coded_label)

    def schematic_from_data(self, current_board_state, grid_size=4):
        """
        Render a schematic representation of the board state and return it as a PIL image object.
        Adds text labels with chess coordinates in unoccupied cells.

        Args:
            current_board_state (list of dict): Board state containing body, color, and current coordinates.

        Returns:
            PIL.Image.Image: Rendered schematic as a PIL image object.
        """

        fig, ax = plt.subplots(figsize=(12, 9), dpi=100)

        # Create a custom colormap with fully transparent cells
        transparent_cmap = mcolors.ListedColormap([(1, 1, 1, 0)])  # RGBA: White color, fully transparent

        # Draw gridlines and format
        sns.heatmap(
            np.zeros((grid_size, grid_size)),  # Empty grid data
            cbar=False, square=True, linewidths=2, linecolor='black',  # Black gridlines
            xticklabels=False, yticklabels=False, ax=ax,
            cmap=transparent_cmap  # Custom transparent colormap
        )

        # Add a custom border around the heatmap
        patch = Rectangle(
            (0, 0), grid_size, grid_size,  # Coordinates and dimensions
            fill=False, edgecolor='black', linewidth=4  # Border color and width
        )
        ax.add_patch(patch)  # Add the rectangle to the axes

        # Customize the border
        for spine in ax.spines.values():
            spine.set_edgecolor('black')  # Set border color
            spine.set_linewidth(10)  # Set border width

        # Make the background transparent
        ax.figure.patch.set_alpha(0)

        # Map shapes to matplotlib markers
        shape_map = {
            'sphere': 'o',  # Circle
            'cube': 's',  # Square
            'pyramid': '^',  # Triangle
            'cylinder': 'H'  # Hexagon
        }

        # Track occupied cells
        occupied_cells = set()

        # Plot each object on the board
        for obj in current_board_state:
            body = obj['body']
            color = obj['color']
            x, y = obj['current_coordinate']

            # Swap x and y to match the grid's coordinate system and flip y to invert the vertical axis
            x, y = grid_size - 1 - y, x

            # Mark this cell as occupied
            occupied_cells.add((x, y))

            # Get the corresponding marker shape or default to a circle
            shape = shape_map.get(body, 'o')
            ax.plot(
                y + 0.5, x + 0.5,  # Center the markers in the cells
                marker=shape, markersize=80, color=color, markeredgecolor='black'
            )

        # Add labels for columns (A, B, C, D) on the x-axis
        ax.set_xticks([i + 0.5 for i in range(grid_size)])
        ax.set_xticklabels(['A', 'B', 'C', 'D'], fontsize=32, color='white')

        # Add labels for rows (1, 2, 3, 4) on the y-axis
        ax.set_yticks([i + 0.5 for i in range(grid_size)])
        ax.set_yticklabels([str(grid_size - i) for i in range(grid_size)], fontsize=32, color='white')

        # Add chess coordinates in unoccupied cells
        for x in range(grid_size):
            for y in range(grid_size):
                if (x, y) not in occupied_cells:  # If the cell is not occupied
                    coord_label = f"{chr(65 + y)}{grid_size - x}"  # Convert to chess notation
                    ax.text(
                        y + 0.5, x + 0.5, coord_label,  # Center the label in the cell
                        ha='center', va='center', fontsize=32, color='white', alpha=1
                    )

        # Adjust the grid to ensure the labels are positioned correctly
        ax.tick_params(left=False, bottom=False)  # Hide default tick marks

        # Add extra space around the heatmap
        plt.subplots_adjust(left=0.25, right=0.8, top=0.90, bottom=0.1)

        # Save or convert the figure with transparency
        fig.patch.set_alpha(0)  # Transparent figure background
        ax.patch.set_alpha(0)  # Transparent axes background

        # Save or convert the figure
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        image = Image.open(buf)

        plt.close(fig)  # Close the figure after saving
        # buf.close()

        # Return the PIL image
        return image

    def image_from_base64(self, payload):
        img_observation = base64.b64decode(payload)
        image = Image.frombytes('RGBA', (1200, 900), img_observation, 'raw')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        return image

    def encode_image_from_pil(self, pil_image):
        """Convert PIL Image to base64 string for API consumption."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def color_code_observation(self, observation, background_color):
        """
        Preprocesses an images by removing transparency and setting a solid background.
        """
        background = Image.new('RGB', observation.size, background_color)
        background.paste(observation, mask=observation.getchannel('A') if 'A' in observation.getbands() else None)
        return background

    def add_action_text(self, image, action_text, color="black"):
        """
        Adds the action text in large red letters with a light white, semi-transparent box behind it
        on the top-right corner of the image, 50 pixels away from the top and right border, with rounded corners.

        Args:
            image (PIL.Image): The image on which to add the action text.
            action_text (str): The action text to add to the image.

        Returns:
            PIL.Image: The image with the action text added.
        """
        # Ensure the image is in RGBA mode (supports transparency)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Try to load a larger font size
        try:
            font = ImageFont.truetype("arial.ttf", 50)  # Increased font size to 80
        except IOError:
            #logging.error("Warning: 'arial.ttf' not found. Using default font.")
            font = ImageFont.load_default()

        # Get text bounding box
        text_bbox = draw.textbbox((0, 0), action_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        # Add extra padding to make the box slightly larger than the text
        box_extra_padding = 20  # Adjust this value to control how much larger the box should be
        border_thickness = 3  # Thickness of the black border

        # Set padding, border offset, and corner radius for rounded edges
        padding = 10
        border_offset = 50
        corner_radius = 20  # Radius for the rounded corners

        # Calculate box and text position (50 pixels from the top and right with additional padding)
        text_x = image.width - text_width - padding - border_offset
        text_y = border_offset
        box_x0 = text_x - padding - box_extra_padding
        box_y0 = text_y - padding - box_extra_padding
        box_x1 = image.width - padding - border_offset + box_extra_padding
        box_y1 = text_y + text_height + padding + box_extra_padding

        # Create a semi-transparent overlay
        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))  # Transparent overlay
        overlay_draw = ImageDraw.Draw(overlay)

        # Draw a black border (slightly larger rectangle)
        overlay_draw.rounded_rectangle(
            [box_x0 - border_thickness, box_y0 - border_thickness,
             box_x1 + border_thickness, box_y1 + border_thickness],
            radius=corner_radius + border_thickness,
            fill=(0, 0, 0, 255)  # Black border
        )

        # Draw a semi-transparent white box with rounded corners (50% transparency)
        overlay_draw.rounded_rectangle(
            [box_x0, box_y0, box_x1, box_y1],
            radius=corner_radius,
            fill=(255, 255, 255, 128)
        )

        # Composite the overlay onto the image
        image = Image.alpha_composite(image, overlay)

        # Draw the text in red on the original image
        draw = ImageDraw.Draw(image)
        draw.text((text_x, text_y), action_text, font=font, fill=color)

        return image


@ObservationModel.register_subclass("geom_board_position_inference")
class ObservationModelGeomBoardPositionInference(ObservationModelGeomBoard):
    def __init__(self, state_data: dict, goal_data: dict, game_params: dict = None):

        super().__init__(state_data, goal_data, game_params)

    @property
    def messages_api_agents(self) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{self.state_representation}"}}]},
        ]
        return messages