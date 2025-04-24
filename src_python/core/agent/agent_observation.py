from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import logging


class Observation:
    """
    Wraps the environment state and supports optional visual processing and prompt generation.
    """

    def __init__(self, state: dict, config: Optional[dict] = None):
        """
        Initializes the Observation with a single-step simulation state.

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

