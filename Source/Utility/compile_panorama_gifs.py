import os
from PIL import Image, ImageDraw, ImageFont


def add_sub_caption(img, caption="caption"):
    """
    Adds a white bar underneath the image with a centered caption.

    Args:
        img (PIL.Image): The input image.
        caption (str): The text to display as a caption.

    Returns:
        PIL.Image: The image with the caption bar added.
    """
    # Ensure the image is in 'RGBA' mode to support transparency
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    # Font settings
    try:
        font = ImageFont.truetype("arial.ttf", 40)  # You can customize the font size and type
    except IOError:
        font = ImageFont.load_default()

    # Calculate the height of the caption bar
    caption_height = 80  # Fixed height for the caption bar
    text_width = ImageDraw.Draw(img).textlength(caption, font=font)
    text_height = ImageDraw.Draw(img).textbbox((0, 0), caption, font=font)[3]

    # Create a new image with space for the caption
    new_img = Image.new('RGBA', (img.width, img.height + caption_height), (255, 255, 255, 255))

    # Paste the original image on top
    new_img.paste(img, (0, 0))

    # Draw the white bar with the caption text
    draw = ImageDraw.Draw(new_img)

    # Draw the text in the center of the white bar
    text_x = (new_img.width - text_width) // 2
    text_y = img.height + (caption_height - text_height) // 2
    draw.text((text_x, text_y), caption, font=font, fill=(0, 0, 0, 255))  # Black text on white background

    return new_img


def compile_panorama_gifs(img_sub_dirs, output_gif="panorama.gif"):
    """
    Create a panorama GIF from images in the specified subdirectories.

    Args:
        img_sub_dirs (dict): A dictionary with subdirectory paths and captions.
        output_gif (str): The output path for the final GIF.
    """
    # Load images from subdirectories
    loaded_images = {key: [] for key in img_sub_dirs}  # Store images by subdirectory key

    for key, subdir_info in img_sub_dirs.items():
        img_dir = subdir_info['dir']
        img_paths = sorted([os.path.join(img_dir, f) for f in os.listdir(img_dir) if f.endswith(".png") or f.endswith(".jpg")])
        for img_path in img_paths:
            img = Image.open(img_path)
            img_with_caption = add_sub_caption(img, caption=subdir_info['caption'])
            loaded_images[key].append(img_with_caption)

    # Check that each subdirectory has the same number of images
    num_images_per_subdir = {key: len(images) for key, images in loaded_images.items()}
    if len(set(num_images_per_subdir.values())) > 1:
        raise ValueError("Subdirectories do not have the same number of images.")

    # Get the total number of images
    num_images = next(iter(num_images_per_subdir.values()))

    frames = []  # To store panorama frames

    for i in range(num_images):
        # Get images from left, middle, and right for the current frame
        left_img = loaded_images['left'][i]
        middle_img = loaded_images['middle'][i]
        right_img = loaded_images['right'][i]

        # Calculate width and height for the panorama image
        white_bar_width = 10  # Width of the white bar between images
        panorama_width = left_img.width + middle_img.width + right_img.width + 2 * white_bar_width
        panorama_height = max(left_img.height, middle_img.height, right_img.height)

        # Create the panorama image
        panorama_img = Image.new('RGB', (panorama_width, panorama_height), (255, 255, 255))  # White background

        # Paste the images side by side
        panorama_img.paste(left_img, (0, 0))  # Paste the left image
        panorama_img.paste(middle_img, (left_img.width + white_bar_width, 0))  # Paste the middle image
        panorama_img.paste(right_img, (left_img.width + middle_img.width + 2 * white_bar_width, 0))  # Paste the right image

        frames.append(panorama_img)  # Add to the list of frames

    # Save the frames as a GIF
    gif_path = os.path.join(output_gif)
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=1000, loop=0)  # Duration per frame is 1000 ms

    print(f"Panorama GIF saved at {gif_path}")

if __name__ == "__main__":
    img_sub_dirs = {
        'left': {'dir': 'obs_1', 'caption': '3x3'},
        'middle': {'dir': 'obs_2', 'caption': '4x4'},
        'right': {'dir': 'obs_3', 'caption': '5x5'}
    }

    compile_panorama_gifs(img_sub_dirs)
