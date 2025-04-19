def color_code_observation(self, observation: Image.Image, background_color=(255, 255, 255)) -> Image.Image:
    """
    Removes transparency by adding a solid background color.

    Args:
        observation (Image.Image): PIL image with possible alpha channel.
        background_color (tuple): RGB background color to apply.

    Returns:
        Image.Image: Image with solid background.
    """
    background = Image.new('RGB', observation.size, background_color)
    background.paste(observation, mask=observation.getchannel('A') if 'A' in observation.getbands() else None)
    return background


def add_action_text(self, image: Image.Image, action_text: str, color="black") -> Image.Image:
    """
    Adds an action label as a semi-transparent box + text overlay in the top-right of an image.

    Args:
        image (PIL.Image): The image to annotate.
        action_text (str): The action text to overlay.
        color (str): Font color.

    Returns:
        PIL.Image: Annotated image.
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
        [box_x0 - border_thickness, box_y0 - border_thickness, box_x1 + border_thickness,
         box_y1 + border_thickness],
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