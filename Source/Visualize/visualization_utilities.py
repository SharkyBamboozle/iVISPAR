import os
import json
import re
from PIL import Image, ImageDraw, ImageFont
import os
from PIL import Image, ImageDraw, ImageFont,ImageSequence
from moviepy import ImageSequenceClip
import numpy as np
import json


def add_background_to_transparent_images(images, background_color=(0, 0, 0)):
    """
    Preprocesses a list of images by removing transparency and setting a solid background.

    Args:
        images (list): List of PIL.Image objects.
        background_color (tuple): RGB color tuple for the background.

    Returns:
        list: List of processed PIL.Image objects with transparency removed.
    """
    processed_images = []
    for image in images:
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, background_color)
            background.paste(image, mask=image.getchannel('A') if 'A' in image.getbands() else None)
            processed_images.append(background)
        else:
            processed_images.append(image)
    return processed_images


def add_action_text(image, action_text, color="black"):
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
        print("Warning: 'arial.ttf' not found. Using default font.")
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


def load_images_and_actions(subdir_path):
    """
    Loads images and extracts the actions from their filenames, excluding 'init'.
    Sorts the filenames based on the numerical order of the frame numbers.

    Args:
        obs_dir (str): Directory containing the observation images.

    Returns:
        tuple: A tuple containing two lists:
            - images (list): List of PIL images.
            - actions (list): List of actions extracted from filenames, excluding 'init'.
    """
    images = []
    actions = []

    obs_dir = os.path.join(subdir_path, "obs")

    # Get all image files from the 'obs' directory, excluding files that end with "_compare.png"
    files = [f for f in os.listdir(obs_dir) if f.endswith(".png") and not f.endswith("_compare.png")]

    # Sort files numerically based on the number in the filename
    files.sort(key=lambda f: int(re.search(r'\d+', f).group()))

    # Iterate over the files to load images and extract actions
    for filename in files:
        image_path = os.path.join(obs_dir, filename)
        image = Image.open(image_path)
        images.append(image)

    # Define the file path
    action_text_file_path = os.path.join(subdir_path, 'agent_message_log.txt')

    # Load the actions from the file as a list of strings
    with open(action_text_file_path, 'r') as file:
        actions = [line.strip() for line in file if line.strip()]  # Remove whitespace and skip empty lines
    #actions.pop() #TODO remove when Astar agent bug is fixed

    return images, actions


def load_params_from_json(file_name):
    """
    Loads parameters from a JSON file and returns them as a dictionary.

    Args:
        file_path (str): Path to the JSON file containing the parameters.

    Returns:
        dict: A dictionary containing all the parameters from the JSON file.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(base_dir, 'Data', 'Params', file_name)
    try:
        with open(file_path, 'r') as file:
            params = json.load(file)
        print(f"Loaded parameters from {file_path} successfully.")
        return params
    except Exception as e:
        print(f"Error loading parameters from {file_path}: {e}")
        return {}

def generate_front_page(text):
    pass

if __name__ == "__main__":

    file_name = "obs_0.png"
    img_path = os.path.join(file_name)
    img = Image.open(img_path)

    color_codes = load_params_from_json('color_codes.json')
    for key, value in color_codes.items():

        imgs_color = add_background_to_transparent_images([img], tuple(color_codes[key]['rgb']))
        img_color = imgs_color[0]

        img_text = add_action_text(img_color, key)

        img_result_path = os.path.join(f"{file_name}_{color_codes[key]['color']}.png")
        img_text.save(img_result_path)