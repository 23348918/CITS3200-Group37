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

def parse_arguments() -> argparse.Namespace:
    """
    @brief Parses command-line arguments for applying filters to an image.
    @return argparse.Namespace: Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Apply filters to an image.")
    parser.add_argument("input_path",
                        type=str,
                        help="Path to the input image."
    )
    parser.add_argument("output",
                        type=str,
                        help="Path/name of output image."
    )
    parser.add_argument("filter",
                        type=str,
                        choices=list(FILTERS.keys()),
                        help="Which filter will be applied to the image."
    )
    parser.add_argument("-s", "--strength",
                        type=float,
                        default=0.5,
                        help="The strength of the filter from 0.0 to 1.0. Default is 0.5."
    )
    return parser.parse_args()  

def main() -> None:
    """
    @brief Main function to parse arguments, apply the selected filter to the image, and save the result.
    @return None
    """
    args: argparse.Namespace = parse_arguments()

    image: Image.Image = Image.open(args.input_path)
    filter_func: Callable[[Image.Image, float], Image.Image] = FILTERS.get(args.filter)
    if not filter_func:
        raise ValueError(f"Unknown filter: {args.filter}")
    
    image = filter_func(image, args.strength)
    image.save(args.output)

if __name__ == "__main__":
    main()
