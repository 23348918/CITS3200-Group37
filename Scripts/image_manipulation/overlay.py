from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, Tuple
from pathlib import Path

OVERLAY_FUNCTIONS: Dict[str, Tuple[float, int]] = {
    "graffiti": (1.2, 15),
    "fog": (4.0, 30),
    "lens-flare": (1.5, 50),
    "rain": (1.0, 20),
    "wet-filter": (1.0, 20)
}

def enhance_overlay(overlay: Image.Image, effect_type: str) -> Image.Image:
    """Enhances the overlay image based on the specified effect type using PIL.
    
    Args:
        overlay: The overlay image to enhance.
        effect_type: The type of effect ('rain', 'fog', 'graffiti', 'lens-flare', 'wet-filter').

    Returns:
        The enhanced overlay image.
    """
    if effect_type not in OVERLAY_FUNCTIONS:
        raise ValueError("Invalid effect type")
    
    alpha, beta = OVERLAY_FUNCTIONS[effect_type]
    enhancer = ImageEnhance.Brightness(overlay)
    overlay = enhancer.enhance(alpha)
    
    # Adjusting contrast for a more pronounced effect
    enhancer = ImageEnhance.Contrast(overlay)
    overlay = enhancer.enhance(beta / 10.0)
    
    return overlay

def process_image_overlay(background: Image.Image, effect_type: str, overlay_path: str) -> Image.Image:
    """Adds a specified overlay effect to a background image using PIL.
    
    Args:
        background: The background image as a PIL Image object.
        effect_type: The type of effect to apply ('rain', 'fog', 'graffiti', 'lens-flare', 'wet-filter').
        overlay_path: Path to the overlay image.

    Returns:
        The processed Image object with the overlay applied.
    """
    overlay = Image.open(overlay_path).convert("RGBA")

    if effect_type == "fog":
        new_size = (int(background.size[0] * 1.8), int(background.size[1] * 1.8))
        overlay = overlay.resize(new_size, Image.Resampling.LANCZOS)
        start_x = (overlay.size[0] - background.size[0]) // 2
        start_y = (overlay.size[1] - background.size[1]) // 2
        overlay = overlay.crop((start_x, start_y, start_x + background.size[0], start_y + background.size[1]))
    else:
        overlay = overlay.resize(background.size, Image.Resampling.LANCZOS)

    overlay = enhance_overlay(overlay, effect_type)

    # Blend the overlay and background
    blended = Image.alpha_composite(background.convert("RGBA"), overlay)
    
    return blended.convert("RGB")

