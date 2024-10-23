import os
from PIL import Image, ImageDraw, ImageFont,ImageSequence
import re

def load_images_and_actions(obs_dir):
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

    # Get all image files from the 'obs' directory
    files = [f for f in os.listdir(obs_dir) if f.endswith(".png")]

    # Sort files numerically based on the number in the filename
    files.sort(key=lambda f: int(re.search(r'\d+', f).group()))

    # Iterate over the files to load images and extract actions
    for filename in files:
        image_path = os.path.join(obs_dir, filename)
        image = Image.open(image_path)
        images.append(image)

        # Extract the action from the filename (exclude 'init')
        action = filename.split("_")[-1].replace(".png", "")
        if action != "init":
            actions.append(action)

    return images, actions


def add_action_text(image, action_text):
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

    # Draw a semi-transparent white box with rounded corners (50% transparency)
    overlay_draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=corner_radius, fill=(255, 255, 255, 128))

    # Composite the overlay onto the image
    image = Image.alpha_composite(image, overlay)

    # Draw the text in red on the original image
    draw = ImageDraw.Draw(image)
    draw.text((text_x, text_y), action_text, font=font, fill="red")

    return image



def generate_gif_from_images_and_actions(images, actions, gif_path, duration=500):
    """
    Generates a GIF from the given list of images and actions, with the specified order of frames.

    Args:
        images (list): List of PIL images.
        actions (list): List of actions corresponding to the images.
        gif_path (str): Path to save the generated GIF.
        duration (int): Duration (in milliseconds) each frame should be displayed.
    """
    frames = []

    # First image (with no text)
    frames.append(images[0].copy())  # Add the first image without text

    # Add the first image again but with its corresponding action text (actions[0])
    if actions:
        annotated_frame_with_first_action = add_action_text(images[0].copy(), actions[0])
        frames.append(annotated_frame_with_first_action)

    # Iterate over the rest of the images and add frames in the desired order
    for i in range(1, len(images)):
        current_image = images[i]

        # Add current image with the previous action (if exists)
        if i - 1 < len(actions):
            annotated_frame_with_previous_action = add_action_text(current_image.copy(), actions[i - 1])
            frames.append(annotated_frame_with_previous_action)

        # Add current image with no text
        frames.append(current_image.copy())

        # Add current image with its own action (if exists)
        if i < len(actions):
            annotated_frame_with_current_action = add_action_text(current_image.copy(), actions[i])
            frames.append(annotated_frame_with_current_action)

    # Save the images as a GIF with the desired frame duration
    try:
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    except Exception as e:
        print(f"Error saving GIF: {e}")


def combine_gif_with_init(gif_path, init_image_path, output_gif_path, duration=1000):
    """
    Combines the GIF with the 'init' image by placing the init image to the right of each GIF frame.
    Saves the combined frames as a new GIF.

    Args:
        gif_path (str): The path to the input GIF file.
        init_image_path (str): The path to the 'init' image.
        output_gif_path (str): The path to save the new combined GIF.
        duration (int): The duration (in milliseconds) for each frame in the GIF.
    """
    # Load the 'init' image
    init_image = Image.open(init_image_path)

    # Load the original GIF
    gif = Image.open(gif_path)

    # List to hold the combined frames
    combined_frames = []

    # Iterate over each frame in the original GIF
    for frame in ImageSequence.Iterator(gif):
        # Ensure the frame has the same mode as the init image
        frame = frame.convert("RGBA")

        # Create a new blank image with enough width to hold both the GIF frame and the init image
        combined_width = frame.width + init_image.width
        combined_height = max(frame.height, init_image.height)
        combined_frame = Image.new("RGBA", (combined_width, combined_height))

        # Paste the GIF frame on the left
        combined_frame.paste(frame, (0, 0))

        # Paste the 'init' image on the right
        combined_frame.paste(init_image, (frame.width, 0))

        # Add the combined frame to the list
        combined_frames.append(combined_frame)

    # Save the combined frames as a new GIF
    combined_frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=combined_frames[1:],
        duration=duration,
        loop=0
    )


def generate_episode_gif(experiment_path, duration=500):
    obs_dir = os.path.join(experiment_path, "obs")

    # Load the images and actions
    images, actions = load_images_and_actions(obs_dir)

    # Generate the GIF
    gif_path = os.path.join(experiment_path, "experiment_results.gif")
    init_image_path = os.path.join(experiment_path, "obs/obs_0_init.png")
    output_gif_path = os.path.join(experiment_path, "experiment_results_compare.gif")

    generate_gif_from_images_and_actions(images, actions,
                                         gif_path=gif_path,
                                         duration=duration)

    combine_gif_with_init(gif_path, init_image_path, output_gif_path, duration=duration)

    print(f"GIF saved at {experiment_path}")


if __name__ == "__main__":
    experiment_path = r"C:\Users\Sharky\Desktop\py_project_RIPPLE\data\experiment_ID_20241023_150158\experiment_UserInteractiveAgent_ShapePuzzle_1"
    generate_episode_gif(experiment_path)
