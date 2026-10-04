from datetime import datetime
from pathlib import Path
from schemas import AdBrief, ColorMood, TextPosition
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from schemas import AdBrief


OUTPUT_DIR = Path("outputs")


PALETTES = {
    "Warm": {
        "start": "#FF8A22",
        "end": "#4A1200",
        "accent": "#FFD6A3",
        "highlight": "#FFF3E4",
        "package": "#FFF5E8",
        "package_text": "#1E1A17",
        "badge": "#FF5A1F",
    },
    "Cool": {
        "start": "#26BDF2",
        "end": "#102B63",
        "accent": "#C9F2FF",
        "highlight": "#EFFCFF",
        "package": "#F4FCFF",
        "package_text": "#10213E",
        "badge": "#0B78B6",
    },
    "Pastel": {
        "start": "#F4B9D7",
        "end": "#8E74D4",
        "accent": "#FFF0F8",
        "highlight": "#FFF8FC",
        "package": "#FFF8FD",
        "package_text": "#31214B",
        "badge": "#AE5D9F",
    },
    "Dark": {
        "start": "#29324F",
        "end": "#080B16",
        "accent": "#D6E4FF",
        "highlight": "#F1F6FF",
        "package": "#F7FAFF",
        "package_text": "#121827",
        "badge": "#6276DE",
    },
    "Brand color": {
        "start": "#FF7A1A",
        "end": "#5C1A00",
        "accent": "#FFE0BB",
        "highlight": "#FFF5E9",
        "package": "#FFF7ED",
        "package_text": "#231A14",
        "badge": "#FF5A1F",
    },
}


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def interpolate_color(
    start: tuple[int, int, int],
    end: tuple[int, int, int],
    progress: float,
) -> tuple[int, int, int]:
    return tuple(
        int(start[index] + (end[index] - start[index]) * progress)
        for index in range(3)
    )


def create_gradient_background(
    width: int,
    height: int,
    start_color: tuple[int, int, int],
    end_color: tuple[int, int, int],
) -> Image.Image:
    image = Image.new("RGB", (width, height))
    pixels = image.load()

    for y in range(height):
        vertical_progress = y / max(height - 1, 1)

        for x in range(width):
            horizontal_progress = x / max(width - 1, 1)

            progress = min(
                1,
                max(
                    0,
                    vertical_progress * 0.78
                    + horizontal_progress * 0.22,
                ),
            )

            pixels[x, y] = interpolate_color(
                start_color,
                end_color,
                progress,
            )

    return image


def get_font(font_size: int, bold: bool = True):
    font_paths = []

    if bold:
        font_paths.extend(
            [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/Arial.ttf",
            ]
        )
    else:
        font_paths.extend(
            [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/Arial.ttf",
            ]
        )

    for font_path in font_paths:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, font_size)

    return ImageFont.load_default()


def get_fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    start_size: int,
    min_size: int,
) -> ImageFont.FreeTypeFont:
    for size in range(start_size, min_size - 1, -2):
        font = get_font(size, bold=True)
        bbox = draw.textbbox((0, 0), text, font=font)

        if bbox[2] - bbox[0] <= max_width:
            return font

    return get_font(min_size, bold=True)


def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    max_width: int,
) -> str:
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        proposed = " ".join(current_line + [word])
        bbox = draw.textbbox((0, 0), proposed, font=font)

        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def add_soft_light(
    image: Image.Image,
    center_x: int,
    center_y: int,
    radius: int,
    color: tuple[int, int, int],
    opacity: int,
) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for current_radius in range(radius, 0, -12):
        progress = 1 - (current_radius / radius)
        alpha = int(opacity * progress * progress)
        draw.ellipse(
            (
                center_x - current_radius,
                center_y - current_radius,
                center_x + current_radius,
                center_y + current_radius,
            ),
            fill=(*color, alpha),
        )

    return Image.alpha_composite(image, overlay)


def draw_energy_streaks(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    accent_color: tuple[int, int, int],
) -> None:
    random.seed(7)

    for index in range(7):
        start_x = random.randint(-width // 5, width)
        start_y = random.randint(height // 3, height)
        end_x = start_x + random.randint(width // 4, width // 2)
        end_y = start_y - random.randint(height // 8, height // 3)

        line_width = max(3, width // 180)

        draw.line(
            (start_x, start_y, end_x, end_y),
            fill=(*accent_color, 45),
            width=line_width,
        )


def draw_nutrition_badge(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    top_text: str,
    bottom_text: str,
    fill_color: tuple[int, int, int],
) -> None:
    draw.rounded_rectangle(
        (x, y, x + width, y + height),
        radius=height // 2,
        fill=fill_color,
    )

    top_font = get_font(max(15, height // 4), bold=True)
    bottom_font = get_font(max(11, height // 6), bold=False)

    top_box = draw.textbbox((0, 0), top_text, font=top_font)
    bottom_box = draw.textbbox((0, 0), bottom_text, font=bottom_font)

    top_width = top_box[2] - top_box[0]
    bottom_width = bottom_box[2] - bottom_box[0]

    draw.text(
        (x + (width - top_width) // 2, y + height * 0.18),
        top_text,
        font=top_font,
        fill=(255, 255, 255),
    )

    draw.text(
        (
            x + (width - bottom_width) // 2,
            y + height * 0.58,
        ),
        bottom_text,
        font=bottom_font,
        fill=(255, 255, 255),
    )


def draw_product_package(
    image: Image.Image,
    brief: AdBrief,
    palette: dict,
    margin: int,
) -> None:
    width, height = image.size
    draw = ImageDraw.Draw(image)

    package_width = int(width * 0.45)
    package_height = int(height * 0.37)
    package_x = (width - package_width) // 2
    package_y = int(height * 0.54)

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.rounded_rectangle(
        (
            package_x + 18,
            package_y + 24,
            package_x + package_width + 18,
            package_y + package_height + 24,
        ),
        radius=max(28, width // 38),
        fill=(0, 0, 0, 110),
    )

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    image.alpha_composite(shadow)

    draw = ImageDraw.Draw(image)

    package_color = hex_to_rgb(palette["package"])
    package_text = hex_to_rgb(palette["package_text"])
    badge_color = hex_to_rgb(palette["badge"])

    draw.rounded_rectangle(
        (
            package_x,
            package_y,
            package_x + package_width,
            package_y + package_height,
        ),
        radius=max(28, width // 38),
        fill=(*package_color, 255),
        outline=(*hex_to_rgb(palette["accent"]), 235),
        width=max(3, width // 260),
    )

    stripe_height = int(package_height * 0.19)

    draw.rounded_rectangle(
        (
            package_x,
            package_y,
            package_x + package_width,
            package_y + stripe_height,
        ),
        radius=max(28, width // 38),
        fill=badge_color,
    )

    draw.rectangle(
        (
            package_x,
            package_y + stripe_height // 2,
            package_x + package_width,
            package_y + stripe_height,
        ),
        fill=badge_color,
    )

    brand_font = get_fit_font(
        draw,
        "FITFUEL",
        int(package_width * 0.76),
        max(26, int(package_width * 0.15)),
        20,
    )

    brand_box = draw.textbbox((0, 0), "FITFUEL", font=brand_font)
    brand_width = brand_box[2] - brand_box[0]

    draw.text(
        (
            package_x + (package_width - brand_width) // 2,
            package_y + int(package_height * 0.08),
        ),
        "FITFUEL",
        font=brand_font,
        fill=(255, 255, 255),
    )

    category_font = get_font(
        max(16, int(package_width * 0.045)),
        bold=False,
    )

    category_text = "PROTEIN BAR"
    category_box = draw.textbbox((0, 0), category_text, font=category_font)
    category_width = category_box[2] - category_box[0]

    draw.text(
        (
            package_x + (package_width - category_width) // 2,
            package_y + int(package_height * 0.29),
        ),
        category_text,
        font=category_font,
        fill=package_text,
    )

    flavor_font = get_font(
        max(17, int(package_width * 0.052)),
        bold=True,
    )

    flavor_text = "CHOCOLATE ALMOND"
    flavor_box = draw.textbbox((0, 0), flavor_text, font=flavor_font)
    flavor_width = flavor_box[2] - flavor_box[0]

    draw.text(
        (
            package_x + (package_width - flavor_width) // 2,
            package_y + int(package_height * 0.42),
        ),
        flavor_text,
        font=flavor_font,
        fill=package_text,
    )

    badge_width = int(package_width * 0.30)
    badge_height = int(package_height * 0.22)
    badge_y = package_y + int(package_height * 0.67)

    draw_nutrition_badge(
        draw,
        package_x + int(package_width * 0.10),
        badge_y,
        badge_width,
        badge_height,
        "20G",
        "PROTEIN",
        badge_color,
    )

    draw_nutrition_badge(
        draw,
        package_x + int(package_width * 0.60),
        badge_y,
        badge_width,
        badge_height,
        "0G",
        "SUGAR",
        package_text,
    )

def draw_fitness_watch(
    image: Image.Image,
    brief: AdBrief,
    palette: dict,
    margin: int,
) -> None:
    """
    Draw a stylized smartwatch for Fitness-category campaigns.
    """

    width, height = image.size
    draw = ImageDraw.Draw(image)

    accent = hex_to_rgb(palette["accent"])
    package_color = hex_to_rgb(palette["package"])
    package_text = hex_to_rgb(palette["package_text"])
    badge = hex_to_rgb(palette["badge"])

    watch_width = int(width * 0.34)
    watch_height = int(height * 0.31)

    watch_x = (width - watch_width) // 2
    watch_y = int(height * 0.56)

    strap_width = int(watch_width * 0.36)
    strap_x = watch_x + (watch_width - strap_width) // 2

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.rounded_rectangle(
        (
            watch_x + 16,
            watch_y + 20,
            watch_x + watch_width + 16,
            watch_y + watch_height + 20,
        ),
        radius=max(32, width // 34),
        fill=(0, 0, 0, 125),
    )

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    image.alpha_composite(shadow)

    draw = ImageDraw.Draw(image)

    # Top and bottom watch strap.
    draw.rounded_rectangle(
        (
            strap_x,
            watch_y - int(height * 0.12),
            strap_x + strap_width,
            watch_y + int(height * 0.04),
        ),
        radius=strap_width // 2,
        fill=(*accent, 245),
    )

    draw.rounded_rectangle(
        (
            strap_x,
            watch_y + watch_height - int(height * 0.04),
            strap_x + strap_width,
            watch_y + watch_height + int(height * 0.12),
        ),
        radius=strap_width // 2,
        fill=(*accent, 245),
    )

    # Watch body.
    draw.rounded_rectangle(
        (
            watch_x,
            watch_y,
            watch_x + watch_width,
            watch_y + watch_height,
        ),
        radius=max(34, width // 30),
        fill=(16, 19, 30, 255),
        outline=(*package_color, 210),
        width=max(3, width // 260),
    )

    screen_padding = int(watch_width * 0.09)

    draw.rounded_rectangle(
        (
            watch_x + screen_padding,
            watch_y + screen_padding,
            watch_x + watch_width - screen_padding,
            watch_y + watch_height - screen_padding,
        ),
        radius=max(24, width // 42),
        fill=(*package_color, 255),
    )

    # Activity rings.
    ring_center_x = watch_x + watch_width // 2
    ring_center_y = watch_y + int(watch_height * 0.47)

    outer_radius = int(watch_width * 0.25)
    middle_radius = int(watch_width * 0.18)
    inner_radius = int(watch_width * 0.11)

    ring_width = max(7, width // 100)

    draw.arc(
        (
            ring_center_x - outer_radius,
            ring_center_y - outer_radius,
            ring_center_x + outer_radius,
            ring_center_y + outer_radius,
        ),
        start=25,
        end=325,
        fill=badge,
        width=ring_width,
    )

    draw.arc(
        (
            ring_center_x - middle_radius,
            ring_center_y - middle_radius,
            ring_center_x + middle_radius,
            ring_center_y + middle_radius,
        ),
        start=75,
        end=340,
        fill=accent,
        width=ring_width,
    )

    draw.arc(
        (
            ring_center_x - inner_radius,
            ring_center_y - inner_radius,
            ring_center_x + inner_radius,
            ring_center_y + inner_radius,
        ),
        start=120,
        end=355,
        fill=(80, 210, 165),
        width=ring_width,
    )

    # Watch brand and activity number.
    brand_font = get_font(max(14, int(width * 0.018)), bold=True)
    activity_font = get_font(max(15, int(width * 0.021)), bold=True)
    label_font = get_font(max(11, int(width * 0.014)), bold=False)

    brand_text = brief.product_name.upper()[:14]
    brand_box = draw.textbbox((0, 0), brand_text, font=brand_font)

    draw.text(
        (
            ring_center_x - (brand_box[2] - brand_box[0]) // 2,
            watch_y + int(watch_height * 0.10),
        ),
        brand_text,
        font=brand_font,
        fill=package_text,
    )

    activity_text = "8,420"
    activity_box = draw.textbbox((0, 0), activity_text, font=activity_font)

    draw.text(
        (
            ring_center_x - (activity_box[2] - activity_box[0]) // 2,
            watch_y + int(watch_height * 0.70),
        ),
        activity_text,
        font=activity_font,
        fill=package_text,
    )

    label_text = "STEPS TODAY"
    label_box = draw.textbbox((0, 0), label_text, font=label_font)

    draw.text(
        (
            ring_center_x - (label_box[2] - label_box[0]) // 2,
            watch_y + int(watch_height * 0.82),
        ),
        label_text,
        font=label_font,
        fill=package_text,
    )


def draw_generic_product_tile(
    image: Image.Image,
    brief: AdBrief,
    palette: dict,
    margin: int,
) -> None:
    """
    Draw a generic branded product tile for categories not yet customized.
    """

    width, height = image.size
    draw = ImageDraw.Draw(image)

    accent = hex_to_rgb(palette["accent"])
    package_color = hex_to_rgb(palette["package"])
    package_text = hex_to_rgb(palette["package_text"])
    badge = hex_to_rgb(palette["badge"])

    tile_width = int(width * 0.43)
    tile_height = int(height * 0.29)
    tile_x = (width - tile_width) // 2
    tile_y = int(height * 0.59)

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    shadow_draw.rounded_rectangle(
        (
            tile_x + 16,
            tile_y + 20,
            tile_x + tile_width + 16,
            tile_y + tile_height + 20,
        ),
        radius=max(28, width // 38),
        fill=(0, 0, 0, 120),
    )

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))
    image.alpha_composite(shadow)

    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (
            tile_x,
            tile_y,
            tile_x + tile_width,
            tile_y + tile_height,
        ),
        radius=max(28, width // 38),
        fill=(*package_color, 255),
        outline=(*accent, 220),
        width=max(3, width // 260),
    )

    icon_size = int(tile_height * 0.34)
    icon_x = tile_x + (tile_width - icon_size) // 2
    icon_y = tile_y + int(tile_height * 0.14)

    draw.rounded_rectangle(
        (
            icon_x,
            icon_y,
            icon_x + icon_size,
            icon_y + icon_size,
        ),
        radius=max(18, icon_size // 4),
        fill=badge,
    )

    icon_font = get_font(max(20, icon_size // 2), bold=True)
    icon_text = brief.product_name[:1].upper()
    icon_box = draw.textbbox((0, 0), icon_text, font=icon_font)

    draw.text(
        (
            icon_x + (icon_size - (icon_box[2] - icon_box[0])) // 2,
            icon_y + (icon_size - (icon_box[3] - icon_box[1])) // 2,
        ),
        icon_text,
        font=icon_font,
        fill=(255, 255, 255),
    )

    product_font = get_fit_font(
        draw,
        brief.product_name.upper(),
        int(tile_width * 0.82),
        max(20, int(tile_width * 0.090)),
        16,
    )

    product_text = brief.product_name.upper()
    product_box = draw.textbbox((0, 0), product_text, font=product_font)

    draw.text(
        (
            tile_x + (tile_width - (product_box[2] - product_box[0])) // 2,
            tile_y + int(tile_height * 0.57),
        ),
        product_text,
        font=product_font,
        fill=package_text,
    )

    category_font = get_font(max(12, int(tile_width * 0.038)), bold=False)
    category_text = brief.category.value.upper()
    category_box = draw.textbbox((0, 0), category_text, font=category_font)

    draw.text(
        (
            tile_x + (tile_width - (category_box[2] - category_box[0])) // 2,
            tile_y + int(tile_height * 0.78),
        ),
        category_text,
        font=category_font,
        fill=(*package_text, 180),
    )


def draw_category_visual(
    image: Image.Image,
    brief: AdBrief,
    palette: dict,
    margin: int,
) -> None:
    """
    Route each campaign category to an appropriate product visual.
    """

    if brief.category.value == "Food":
        draw_product_package(
            image=image,
            brief=brief,
            palette=palette,
            margin=margin,
        )
    elif brief.category.value == "Fitness":
        draw_fitness_watch(
            image=image,
            brief=brief,
            palette=palette,
            margin=margin,
        )
    else:
        draw_generic_product_tile(
            image=image,
            brief=brief,
            palette=palette,
            margin=margin,
        )

def compose_banner(
    brief: AdBrief,
    tagline: str,
) -> dict:
    """
    Create a polished synthetic campaign banner.

    This is an intentional fallback visual. Later you can provide an
    SDXL/API background image while keeping the typography and layout logic.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)

    width, height = brief.dimensions
    palette = PALETTES[brief.color_mood.value]

    start_color = (
        hex_to_rgb(brief.brand_hex)
        if brief.brand_hex
        else hex_to_rgb(palette["start"])
    )

    end_color = hex_to_rgb(palette["end"])
    accent_color = hex_to_rgb(palette["accent"])
    highlight_color = hex_to_rgb(palette["highlight"])

    image = create_gradient_background(
        width=width,
        height=height,
        start_color=start_color,
        end_color=end_color,
    ).convert("RGBA")

    image = add_soft_light(
        image=image,
        center_x=width // 2,
        center_y=int(height * 0.24),
        radius=int(width * 0.45),
        color=highlight_color,
        opacity=55,
    )

    image = add_soft_light(
        image=image,
        center_x=int(width * 0.82),
        center_y=int(height * 0.78),
        radius=int(width * 0.32),
        color=accent_color,
        opacity=45,
    )

    draw = ImageDraw.Draw(image)
    draw_energy_streaks(
        draw=draw,
        width=width,
        height=height,
        accent_color=accent_color,
    )

    margin = max(42, int(width * 0.07))
    text_width_limit = width - margin * 2
    start_font_size = max(38, int(width * 0.073))

    headline_font = get_fit_font(
        draw,
        tagline,
        text_width_limit,
        start_font_size,
        max(28, int(width * 0.038)),
    )

    wrapped_tagline = wrap_text(
        draw=draw,
        text=tagline,
        font=headline_font,
        max_width=text_width_limit,
    )

    line_spacing = int(headline_font.size * 0.20)

    text_box = draw.multiline_textbbox(
        (0, 0),
        wrapped_tagline,
        font=headline_font,
        spacing=line_spacing,
    )

    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]

    if brief.text_position.value == "Bottom":
        text_y = int(height * 0.66)
    elif brief.text_position.value == "Center":
        text_y = int(height * 0.34)
    else:
        text_y = margin

    text_x = margin
    panel_padding_x = max(20, int(width * 0.025))
    panel_padding_y = max(18, int(height * 0.020))

    panel_box = (
        text_x - panel_padding_x,
        text_y - panel_padding_y,
        min(width - margin, text_x + text_width + panel_padding_x),
        text_y + text_height + panel_padding_y,
    )

    panel_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel_overlay)

    panel_draw.rounded_rectangle(
        panel_box,
        radius=max(18, int(width * 0.025)),
        fill=(15, 12, 10, 150),
    )

    image = Image.alpha_composite(image, panel_overlay)
    draw = ImageDraw.Draw(image)

    eyebrow_font = get_font(
        max(15, int(width * 0.018)),
        bold=True,
    )

    eyebrow_text = brief.category.value.upper()
    eyebrow_box = draw.textbbox((0, 0), eyebrow_text, font=eyebrow_font)

    draw.text(
        (
            text_x,
            max(10, text_y - int(headline_font.size * 0.75)),
        ),
        eyebrow_text,
        font=eyebrow_font,
        fill=accent_color,
    )

    draw.multiline_text(
        (text_x, text_y),
        wrapped_tagline,
        font=headline_font,
        fill=(255, 255, 255),
        spacing=line_spacing,
    )

    cta_text = brief.cta.value.upper()

    if cta_text != "NONE":
        cta_font = get_font(max(16, int(width * 0.020)), bold=True)
        cta_box = draw.textbbox((0, 0), cta_text, font=cta_font)

        cta_width = (cta_box[2] - cta_box[0]) + int(width * 0.055)
        cta_height = (cta_box[3] - cta_box[1]) + int(height * 0.026)

        cta_x = margin
        cta_y = text_y + text_height + int(height * 0.045)

        draw.rounded_rectangle(
            (
                cta_x,
                cta_y,
                cta_x + cta_width,
                cta_y + cta_height,
            ),
            radius=cta_height // 2,
            fill=(*accent_color, 245),
        )

        draw.text(
            (
                cta_x + int(width * 0.027),
                cta_y + int(height * 0.012),
            ),
            cta_text,
            font=cta_font,
            fill=(25, 25, 25),
        )

    draw_category_visual(
        image=image,
        brief=brief,
        palette=palette,
        margin=margin,
    )

    bottom_font = get_font(
        max(13, int(width * 0.015)),
        bold=False,
    )

    bottom_text = brief.usp.upper()
    bottom_box = draw.textbbox((0, 0), bottom_text, font=bottom_font)
    bottom_width = bottom_box[2] - bottom_box[0]

    draw.text(
        (
            (width - bottom_width) // 2,
            height - margin * 0.55,
        ),
        bottom_text,
        font=bottom_font,
        fill=(*accent_color, 230),
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    safe_product = "".join(
        character.lower()
        if character.isalnum()
        else "_"
        for character in brief.product_name
    ).strip("_")

    output_path = OUTPUT_DIR / f"{safe_product}_{timestamp}.png"

    image.convert("RGB").save(output_path, format="PNG")

    return {
        "output_path": str(output_path),
        "dimensions": (width, height),
        "tagline": tagline,
        "wrapped_tagline": wrapped_tagline,
        "panel_box": panel_box,
        "tagline_character_count": len(tagline),
    }

def compose_banner_variants(
    brief: AdBrief,
    tagline: str,
) -> list[dict]:
    """
    Create visual variations from one Critic-approved tagline.
    """

    from copy import deepcopy

    position_cycle = [
        "Top",
        "Center",
        "Bottom",
        "Top",
        "Center",
    ]

    color_cycle = [
        brief.color_mood.value,
        "Dark",
        "Cool",
        "Warm",
        "Pastel",
    ]

    variants = []

    for index in range(brief.num_variants):
        variant_brief = deepcopy(brief)

        variant_brief.text_position = TextPosition(
            position_cycle[index]
        )

        variant_brief.color_mood = ColorMood(
            color_cycle[index]
        )

        result = compose_banner(
            brief=variant_brief,
            tagline=tagline,
        )

        result["variant_number"] = index + 1
        result["variant_position"] = variant_brief.text_position.value
        result["variant_color_mood"] = variant_brief.color_mood.value

        variants.append(result)

    return variants