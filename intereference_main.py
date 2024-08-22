import argparse
from PIL import Image
from filters import darkness_filter, brightness_filter, gaussian_blur_filter, intensity_filter, motion_blur_filter
from typing import Callable, Dict

FILTERS: Dict[str, Callable[[Image.Image, float], Image.Image]] = {
    "darkness": darkness_filter,
    "brightness": brightness_filter,
    "gaussian": gaussian_blur_filter,
    "intensity": intensity_filter,
    "motion": motion_blur_filter,
}

def main() -> None:
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Apply filters to an image.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input image.")
    parser.add_argument("-o", "--output", required=True, help="Path to save the output image.")
    parser.add_argument("-f", "--filter", required=True, help="Filter to apply. Choose from: darkness, brightness, gaussian, intensity, motion.")
    parser.add_argument("-s", "--strength", type=float, default=0.5, help="The strength of the filter from 0.0 to 1.0. Default is 0.5.")

    args = parser.parse_args()

    # Map filter names to filter functions


    # Load the input image
    image = load_image(args.input)

    # Apply the selected filter
    filter_func = FILTERS.get(args.filter)
    if filter_func:
        image = filter_func(image, args.strength)
    else:
        raise ValueError(f"Unknown filter: {args.filter}")

    # Save the output image
    save_image(image, args.output)

def load_image(path: str) -> Image.Image:
    try:
        image = Image.open(path)
        return image
    except IOError:
        raise ValueError(f"Cannot load image at {path}")

def save_image(image: Image.Image, path: str) -> None:
    try:
        image.save(path)
    except IOError:
        raise ValueError(f"Cannot save image at {path}")

if __name__ == "__main__":
    main()
