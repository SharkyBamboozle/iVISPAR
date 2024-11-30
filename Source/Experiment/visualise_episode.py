import os
from PIL import Image, ImageDraw, ImageFont,ImageSequence
import re

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

    # Get all image files from the 'obs' directory, excluding files that end with "_compare.png"
    files = [f for f in os.listdir(obs_dir) if f.endswith(".png") and not f.endswith("_compare.png")]

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


def add_action_text(image, action_text, color="red"):
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


def generate_gif_from_images_and_actions(images, actions):
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
    #frames.append(images[0].copy())  # Add the first image without text

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

    return frames


def combine_gif_with_init(gif_path, init_image_path, output_gif_path, duration=1000, white_bar_width=20):
    """
    Combines the GIF with the 'init' image by placing the init image to the right of each GIF frame,
    separated by a white bar. Saves the combined frames as a new GIF.

    Args:
        gif_path (str): The path to the input GIF file.
        init_image_path (str): The path to the 'init' image.
        output_gif_path (str): The path to save the new combined GIF.
        duration (int): The duration (in milliseconds) for each frame in the GIF.
        white_bar_width (int): The width of the white bar separating the two images.
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

        # Create a new blank image with enough width to hold both the GIF frame and the init image, plus the white bar
        combined_width = frame.width + init_image.width + white_bar_width
        combined_height = max(frame.height, init_image.height)
        combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))  # White background

        # Paste the GIF frame on the left
        combined_frame.paste(frame, (0, 0))

        # Paste the 'init' image on the right, leaving space for the white bar
        combined_frame.paste(init_image, (frame.width + white_bar_width, 0))

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


def visualise_episode_interaction(experiment_id, duration=500):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)

    # Iterate through subdirectories of the experiment directory
    for subdir in os.listdir(experiment_dir):
        subdir_path = os.path.join(experiment_dir, subdir)

        if not os.path.isdir(subdir_path):
            continue  # Skip non-directory files

        obs_dir = os.path.join(subdir_path, "obs")

        # Load the images and actions
        images, actions = load_images_and_actions(obs_dir)

        init_image_path = os.path.join(experiment_path, "obs/obs_1_init.png")
        output_gif_path = os.path.join(experiment_path, "experiment_results_compare.gif")

        # Preprocess the images to remove transparency
        background_color = (0,0,0)
        images = add_background_to_transparent_images(images, background_color)

        frames = generate_gif_from_images_and_actions(images, actions)

        # Locate the JSON file in the subdirectory
        json_file = next((f for f in os.listdir(subdir_path) if f.startswith('config') and f.endswith('.json')), None)
        if not json_file:
            print(f"No config JSON file found in {subdir_path}. Skipping...")
            continue

        # Extract the base name of the JSON file (without extension)
        json_base_name = os.path.splitext(json_file)[0]
        gif_path = os.path.join(subdir_path, f"{json_base_name}.gif")

        # Save the images as a GIF with the desired frame duration
        try:
            frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
        except Exception as e:
            print(f"Error saving GIF: {e}")

        #combine_gif_with_init(gif_path, init_image_path, output_gif_path, duration=duration)

        print(f"GIF saved at {experiment_path}")


def visualize_state_combination(experiment_id, white_bar_width=20):
    """
    Visualizes the state combination by combining the initial state image and the goal state image
    into a single image with a white bar separating them. Adds text annotations to label the states.

    Args:
        experiment_id (str): The ID of the experiment directory.
        white_bar_width (int): The width of the white bar separating the images.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)

    # Iterate through subdirectories of the experiment directory
    for subdir in os.listdir(experiment_dir):
        subdir_path = os.path.join(experiment_dir, subdir)

        if not os.path.isdir(subdir_path):
            continue  # Skip non-directory files

        # Paths for the images
        init_state_image_path = os.path.join(subdir_path, "obs/obs_1_init.png")
        goal_state_image_path = os.path.join(subdir_path, "obs/obs_2_start.png")

        # Ensure the images exist
        if not os.path.exists(init_state_image_path) or not os.path.exists(goal_state_image_path):
            print(f"Missing images in {subdir_path}. Skipping...")
            continue

        # Load the images
        init_image = Image.open(init_state_image_path)
        init_image = add_action_text(init_image.copy(), "Init", "green")
        goal_image = Image.open(goal_state_image_path)
        goal_image = add_action_text(goal_image.copy(), "goal", "red")

        # Locate the JSON file in the subdirectory
        json_file = next((f for f in os.listdir(subdir_path) if f.startswith('config') and f.endswith('.json')), None)
        if not json_file:
            print(f"No config JSON file found in {subdir_path}. Skipping...")
            continue

        # Extract the base name of the JSON file (without extension)
        json_base_name = os.path.splitext(json_file)[0]

        # Combine the images with a white bar in the middle
        combined_width = init_image.width + goal_image.width + white_bar_width
        combined_height = max(init_image.height, goal_image.height)
        combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))  # White background

        # Paste the 'init' image on the left
        combined_frame.paste(init_image, (0, 0))

        # Paste the 'goal' image on the right, leaving space for the white bar
        combined_frame.paste(goal_image, (init_image.width + white_bar_width, 0))

        # Save the combined image
        img_file_path = os.path.join(subdir_path, f"{json_base_name}.png")
        combined_frame.save(img_file_path)
        print(f"Saved combined image to {img_file_path}")



if __name__ == "__main__":
    #experiment_path = r"C:\Users\Sharky\RIPPLE\Data\Experiments\experiment_ID_20241130_174036\experiment_AStarAgent_SlidingGeomPuzzle_1"
    experiment_path = r"C:\Users\Sharky\RIPPLE\Data\Experiments\experiment_ID_20241130_175532\experiment_AStarAgent_SlidingGeomPuzzle_1"

    visualise_episode_interaction("experiment_ID_20241130_175532")
    visualize_state_combination("experiment_ID_20241130_175532")
