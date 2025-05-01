from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import logging
import json
import base64
import os

class Observation:
    """
    Wraps the environment state and supports optional visual processing and prompt generation.
    """

    def __init__(self, state: dict, config: Optional[dict] = None):
        """
        Initializes the ObservationModel with a single-step simulation state.

        Args:
            state (dict): The state dict containing one "step X" key with metadata.
            config (dict, optional): Experiment/game config to control representation logic.
        """
        self.state = state
        self.step_key = next(iter(state))
        self.step_data = state[self.step_key]
        self.config = config or {}

        # self.instruction_prompt = self.load_prompt_from_md(config["instruction_prompt_file_path"])
        # self.chain_of_thought_prompt = self.load_prompt_from_md(config["cot_prompt_file_path"])

    def get_board_state(self) -> list[str]:
        return self.step_data.get("board_state", [])

    def get_board_data(self) -> list[dict]:
        return self.step_data.get("board_data", [])

    def get_step_index(self) -> int:
        return int(self.step_key.split(" ")[1])

    def get_game_done_flag(self) -> bool:
        return self.step_data.get("game_done", False)

    def color_code_observation(self, observation: Image.Image, background_color=(255, 255, 255)) -> Image.Image:
        """
        Removes transparency by adding a solid background color.
        """
        background = Image.new('RGB', observation.size, background_color)
        background.paste(observation, mask=observation.getchannel('A') if 'A' in observation.getbands() else None)
        return background

    def add_action_text(self, image: Image.Image, action_text: str, color="black") -> Image.Image:
        """
        Adds an action label as a semi-transparent box + text overlay in the top-right of an image.
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except IOError:
            logging.warning("Fallback font: 'arial.ttf' not found.")
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), action_text, font=font)
        text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

        padding = 10
        border_offset = 50
        box_extra_padding = 20
        corner_radius = 20
        border_thickness = 3

        text_x = image.width - text_width - padding - border_offset
        text_y = border_offset
        box_x0 = text_x - padding - box_extra_padding
        box_y0 = text_y - padding - box_extra_padding
        box_x1 = image.width - padding - border_offset + box_extra_padding
        box_y1 = text_y + text_height + padding + box_extra_padding

        overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        overlay_draw.rounded_rectangle(
            [box_x0 - border_thickness, box_y0 - border_thickness, box_x1 + border_thickness, box_y1 + border_thickness],
            radius=corner_radius + border_thickness,
            fill=(0, 0, 0, 255)
        )

        overlay_draw.rounded_rectangle(
            [box_x0, box_y0, box_x1, box_y1],
            radius=corner_radius,
            fill=(255, 255, 255, 128)
        )

        image = Image.alpha_composite(image, overlay)
        draw = ImageDraw.Draw(image)
        draw.text((text_x, text_y), action_text, font=font, fill=color)

        return image

    # def load_prompt_from_md(self, file_path: str) -> str:
    #     # Use your FilePathHandler or PromptLoader here to read markdown content
    #     return FileHandler.read_md(file_path)

    def decode_state(self, response):
        """
        Process a response from the simulation.
        Args:
            sim_message (str or dict): The message from the simulation.
        """

        sim_message = response.get("messages")[0]
        try:
            # Check if sim_message is a string and parse it as JSON
            if isinstance(sim_message, str):
                sim_message = json.loads(sim_message)

            if isinstance(sim_message, dict):
                self.is_done = sim_message.get("game_done", False)
                step_key = f"step {i}"  # Create the step key as "step 1", "step 2", etc.
                self.sim_message_log[step_key] = sim_message  # Add the message to the log
            else:
                logging.error("Invalid simulation message format. Must be a dictionary after parsing.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding simulation message: {e}")

        # add 2D modality
        if self.representation_type=='vision' or self.representation_type == 'text':
            encoded_data = response.get("payload")
            img_observation = base64.b64decode(encoded_data)
            image = Image.frombytes('RGBA', (1200, 900), img_observation, 'raw')
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

            filename = os.path.join(self.obs_dir, f"obs_{i}_3D")

        elif self.representation_type=='schematic':
            image = render_schematic(sim_message.get("board_data", []))

            encoded_data = response.get("payload")
            img_observation = base64.b64decode(encoded_data)
            image2 = Image.frombytes('RGBA', (1200, 900), img_observation, 'raw')
            image2 = image2.transpose(Image.FLIP_TOP_BOTTOM)

            filename = os.path.join(self.obs_dir, f"obs_{i}_2D")
            filename2 = os.path.join(self.obs_dir, f"obs_{i}_3D")

            try:
                filename2 = f"{filename2}.png"
                image2.save(filename2)  # Save the image as a PNG
            except Exception as e:
                logging.error(f"Error saving image to {filename2}: {e}")

        else:
            raise Exception(f"Unknown representation type: {self.representation_type}")


        # Save the image as a PNG file
        try:
            image_path = f"{filename}.png"
            image.save(image_path)  # Save the image as a PNG
        except Exception as e:
            logging.error(f"Error saving image to {filename}: {e}")

        current_board_state = ""
        if isinstance(sim_message, dict):
            # Extract the board checkpoint_state
            current_board_state = sim_message.get("board_state", [])

            # Save the board checkpoint_state as a JSON file
            try:
                json_path = f"{filename}.json"
                with open(json_path, 'w') as f:
                    json.dump(current_board_state, f, indent=4)
            except Exception as e:
                logging.error(f"Error saving board state to {filename}.json: {e}")


        return current_board_state if self.representation_type=='text' else image