import os
from PIL import Image, ImageDraw, ImageFont,ImageSequence
from moviepy import ImageSequenceClip
import numpy as np
import json

from visualization_utilities import add_background_to_transparent_images, add_action_text, load_images_and_actions

def generate_gif_from_images_and_actions2(images, actions):
    """
    Generates a GIF from the given list of images and actions, with optimized color and quality.

    Args:
        images (list): List of PIL images.
        actions (list): List of actions corresponding to the images.
        gif_path (str): Path to save the generated GIF.
        duration (int): Duration (in milliseconds) each frame should be displayed.
    """
    frames = []

    # Add annotated and plain frames
    for i, image in enumerate(images):
        if i < len(actions):
            annotated_frame = add_action_text(image.copy(), actions[i])
            frames.append(annotated_frame)  # Keep original colors
        frames.append(image.copy())  # Keep original colors

    return frames




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


def visualise_episode_interaction(experiment_id, dual=True, white_bar_width=20, duration=600, fps=2.0):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id, 'Episodes')

    # Iterate through subdirectories of the experiment directory
    for subdir in os.listdir(experiment_dir):
        subdir_path = os.path.join(experiment_dir, subdir)

        if not os.path.isdir(subdir_path):
            continue  # Skip non-directory files

        # Load the images and actions
        images, actions = load_images_and_actions(subdir_path)

        #init_image_path = os.path.join(experiment_path, "obs/obs_1_init.png")
        #output_gif_path = os.path.join(experiment_path, "experiment_results_compare.gif")

        # Preprocess the images to remove transparency
        background_color = (82, 138, 174)
        images = add_background_to_transparent_images(images, background_color)

        frames = generate_gif_from_images_and_actions(images, actions)

        if dual:
            #add goal image
            goal_state_image_path = os.path.join(subdir_path, "obs/obs_0.png")
            goal_image = Image.open(goal_state_image_path)
            goal_image = add_background_to_transparent_images([goal_image.copy()], background_color=(100, 191, 106))
            goal_image = goal_image[0] #bcs add_background_to_transparent_images needs list and returns list
            goal_image = add_action_text(goal_image.copy(), "goal", "green")

            dual_frames = []
            for frame in frames:
                # Combine the images with a white bar in the middle
                combined_width = frame.width + goal_image.width + white_bar_width
                combined_height = max(frame.height, goal_image.height)
                combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))  # White background

                # Paste the 'init' image on the left
                combined_frame.paste(frame, (0, 0))

                # Paste the 'goal' image on the right, leaving space for the white bar
                combined_frame.paste(goal_image, (frame.width + white_bar_width, 0))
                dual_frames.append(combined_frame)
            frames = dual_frames


        # Locate the JSON file in the subdirectory
        json_file = next((f for f in os.listdir(subdir_path) if f.startswith('config') and f.endswith('.json')), None)
        if not json_file:
            print(f"No config JSON file found in {subdir_path}. Skipping...")
            continue

        # Extract the base name of the JSON file (without extension)
        json_base_name = os.path.splitext(json_file)[0]
        gif_path = os.path.join(subdir_path, f"{json_base_name}.gif")

        mp4_path = os.path.join(subdir_path, f"play_log.mp4")

        # Ensure all images are converted to RGB numpy arrays
        frames_mp4 = [np.array(img.convert("RGB")) for img in frames]
        clip = ImageSequenceClip([np.array(frame) for frame in frames_mp4], fps=fps)

        # Save the images as a GIF with the desired frame duration
        try:
            #frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=duration, loop=0)
            clip.write_videofile(mp4_path, codec="libx264")

            # #Save the GIF with optimization
            # frames[0].save(
            #      gif_path,
            #      save_all=True,
            #      append_images=frames[1:],
            #      duration=duration,
            #      loop=0,
            #      optimize=False,
            #  )
        except Exception as e:
            print(f"Error saving GIF: {e}")

        #combine_gif_with_init(gif_path, init_image_path, output_gif_path, duration=duration)

        print(f"GIF saved at {subdir_path}")

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
                combined_frame = Image.new("RGBA", (combined_width, combined_height),
                                           (255, 255, 255, 255))  # White background

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


if __name__ == "__main__":
    #experiment_GPT4Agent_InteractivePuzzle_config_SGP_ID_20241203_105154_b_4_g_4_c1_10_c2_0_i_1
    experiment_id = "qwen_text_test"

    print(f"Visualise experiment {experiment_id}")
    visualise_episode_interaction(experiment_id)