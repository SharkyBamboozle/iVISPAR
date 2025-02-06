from PIL import Image

from visualization_utilities import add_action_text, add_background_to_transparent_images, load_params_from_json

def create_panorama_image(init_state_image_path, result_state_image_path, goal_state_image_path, output_path, white_bar_width=10, color_codes=None):
    """
    Create a panorama image by combining three images (initial state, result state, goal state)
    side by side with white bars in between.

    Args:
        init_state_image_path (str): Path to the initial state image.
        result_state_image_path (str): Path to the result state image.
        goal_state_image_path (str): Path to the goal state image.
        output_path (str): Path to save the combined panorama image.
        white_bar_width (int, optional): Width of the white bar separating images. Defaults to 10.
        color_codes (dict, optional): Dictionary containing RGB colors and text for annotations.
                                      Example format:
                                      {
                                          'start': {'rgb': (255, 255, 255), 'type': 'Start'},
                                          'last': {'rgb': (200, 200, 200), 'type': 'Last'},
                                          'goal_1': {'rgb': (150, 150, 150), 'type': 'Goal'}
                                      }
    """
    # Ensure color codes are provided
    if color_codes is None:
        color_codes = {
            'start': {'rgb': (255, 255, 255), 'type': 'Start'},
            'last': {'rgb': (200, 200, 200), 'type': 'Last'},
            'goal_1': {'rgb': (150, 150, 150), 'type': 'Goal'}
        }

    # Load and annotate images
    def prepare_image(image_path, annotation):
        return Image.open(image_path)

    init_image = prepare_image(init_state_image_path, 'start')
    result_image = prepare_image(result_state_image_path, 'last')
    goal_image = prepare_image(goal_state_image_path, 'goal_1')

    # Calculate combined dimensions
    combined_width = init_image.width + result_image.width + goal_image.width + 2 * white_bar_width
    combined_height = max(init_image.height, result_image.height, goal_image.height)
    combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))

    # Paste images side by side with white bars separating them
    combined_frame.paste(init_image, (0, 0))
    combined_frame.paste(result_image, (init_image.width + white_bar_width, 0))
    combined_frame.paste(goal_image, (init_image.width + result_image.width + 2 * white_bar_width, 0))

    # Save the combined image
    combined_frame.save(output_path)
    print(f"Panorama image saved at: {output_path}")


from PIL import Image

def create_vertical_stack(image1_path, image2_path, output_path, white_bar_height=10):
    """
    Create a vertical stack of two images with a white bar separating them.

    Args:
        image1_path (str): Path to the first image (top image).
        image2_path (str): Path to the second image (bottom image).
        output_path (str): Path to save the combined vertical image.
        white_bar_height (int, optional): Height of the white bar separating images. Defaults to 10.
    """
    # Load images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Calculate combined dimensions
    combined_width = max(image1.width, image2.width)
    combined_height = image1.height + image2.height + white_bar_height

    # Create a blank canvas with a white background
    combined_frame = Image.new("RGBA", (combined_width, combined_height), (255, 255, 255, 255))

    # Paste the first image at the top
    combined_frame.paste(image1, (0, 0))

    # Paste the second image at the bottom, separated by the white bar
    combined_frame.paste(image2, (0, image1.height + white_bar_height))

    # Save the combined image
    combined_frame.save(output_path)
    print(f"Vertical stacked image saved at: {output_path}")


if __name__ == "__main__":
    init_image_path = "2_past.png"
    result_image_path = "2_current.png"
    goal_image_path = "2_goal.png"
    output_image_path = "panorama_states.png"

    create_panorama_image(init_image_path, result_image_path, goal_image_path, output_image_path)


    image1_path = "panorama_states_3D.png"
    image2_path = "panorama_states_2D.png"
    output_image_path = "vertical_stack.png"

    create_vertical_stack(image1_path, image2_path, output_image_path)