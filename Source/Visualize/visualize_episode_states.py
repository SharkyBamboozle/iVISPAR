from PIL import Image
import os

from visualization_utilities import add_action_text, add_background_to_transparent_images, load_params_from_json


def visualize_full_state_progression(experiment_id, white_bar_width=20):
    """
    Visualizes the full state progression by combining the initial state, last observed state,
    and goal state into a single 3x1 image with white bars separating them.

    Args:
        experiment_id (str): The ID of the experiment directory.
        white_bar_width (int): The width of the white bar separating the images.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    episode_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id, 'Episodes')
    color_codes = load_params_from_json('color_codes.json')

    # Iterate through subdirectories of the experiment directory
    for subdir in os.listdir(episode_dir):
        subdir_path = os.path.join(episode_dir, subdir)

        if not os.path.isdir(subdir_path):
            continue  # Skip non-directory files

        obs_dir = os.path.join(subdir_path, "obs")

        if not os.path.exists(obs_dir):
            print(f"No 'obs' directory found in {subdir_path}. Skipping...")
            continue

        obs_files = [f for f in os.listdir(obs_dir) if f.startswith('obs_') and f.endswith('.png')]

        if not obs_files:
            print(f"No 'obs_*.png' files found in {obs_dir}. Skipping...")
            continue

        # Paths for initial, goal, and result state images
        init_state_image_path = os.path.join(obs_dir, "obs_1.png")
        goal_state_image_path = os.path.join(obs_dir, "obs_0.png")

        # Extract numbers from filenames to find the highest for the last observed state
        obs_numbers = [int(f.split('_')[1].split('.')[0]) for f in obs_files if f.split('_')[1].split('.')[0].isdigit()]
        max_obs_number = max(obs_numbers)
        result_state_image_path = os.path.join(obs_dir, f"obs_{max_obs_number}.png")

        # Ensure all images exist
        if not all(os.path.exists(path) for path in [init_state_image_path, goal_state_image_path, result_state_image_path]):
            print(f"Missing images in {subdir_path}. Skipping...")
            continue

        # Load and annotate images
        init_image = Image.open(init_state_image_path)
        init_image = add_background_to_transparent_images([init_image.copy()], tuple(color_codes['start']['rgb']))
        init_image = init_image[0]
        init_image = add_action_text(init_image.copy(), color_codes['start']['type'], "black")

        result_image = Image.open(result_state_image_path)
        result_image = add_background_to_transparent_images([result_image.copy()], tuple(color_codes['last']['rgb']))
        result_image = result_image[0]
        result_image = add_action_text(result_image.copy(),  color_codes['last']['type'], "black")

        goal_image = Image.open(goal_state_image_path)
        goal_image = add_background_to_transparent_images([goal_image.copy()], tuple(color_codes['goal_1']['rgb']))
        goal_image = goal_image[0]
        goal_image = add_action_text(goal_image.copy(), color_codes['goal_1']['type'], "black")

        # Combine the three images with white bars in between
        combined_width = init_image.width + result_image.width + goal_image.width + 2 * white_bar_width
        combined_height = max(init_image.height, result_image.height, goal_image.height)
        combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))

        # Paste images side by side with white bars separating them
        combined_frame.paste(init_image, (0, 0))
        combined_frame.paste(result_image, (init_image.width + white_bar_width, 0))
        combined_frame.paste(goal_image, (init_image.width + result_image.width + 2 * white_bar_width, 0))

        # Save the combined image
        img_file_path = os.path.join(subdir_path, f"states_visual.png")
        combined_frame.save(img_file_path)
        print(f"Saved combined image to {img_file_path}")


if __name__ == "__main__":
    #experiment_GPT4Agent_InteractivePuzzle_config_SGP_ID_20241203_105154_b_4_g_4_c1_10_c2_0_i_1
    experiment_id = "qwen_text_test"

    print(f"Visualise experiment {experiment_id}")
    visualize_full_state_progression(experiment_id)