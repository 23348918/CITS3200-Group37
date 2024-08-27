import argparse
from PIL import Image
from filters import darkness_filter, brightness_filter, gaussian_blur_filter, intensity_filter, motion_blur_filter
from typing import Callable, Dict, Tuple, Iterator
import os

FILTERS: Dict[str, Callable[[Image.Image, float], Image.Image]] = {
    "darkness": darkness_filter,
    "brightness": brightness_filter,
    "gaussian": gaussian_blur_filter,
    "intensity": intensity_filter,
    "motion": motion_blur_filter,
}

VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.heic', '.heif', 
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

def parse_arguments() -> argparse.Namespace:
    """
    @brief Parses command-line arguments for applying filters to an image.
    @return argparse.Namespace: Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Apply filters to an image.")
    parser.add_argument("input_path",
                        type=str,
                        help="Path to the input directory."
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

def directory_iterator(directory: str) -> Iterator[Tuple[str, str]]:
    """
    @brief Creates an iterator that yields valid files from a directory and its subdirectories.
    @return Iterator[Tuple[str, str]]: An iterator that yields tuples of (directory_path, file_name) for valid files.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                yield (root, file)

def main() -> None:
    """
    @brief Main function to parse arguments, apply the selected filter to the image, and save the result.
    @return None
    """
    args: argparse.Namespace = parse_arguments()

    for dir_path, file_name in directory_iterator(args.input_path):
        image: Image.Image = Image.open(os.path.join(dir_path, file_name))
        filter_func: Callable[[Image.Image, float], Image.Image] = FILTERS.get(args.filter)
        if not filter_func:
            raise ValueError(f"Unknown filter: {args.filter}")
        
        image = filter_func(image, args.strength)
        image.save(f"Output/{args.filter}_{file_name}")

if __name__ == "__main__":
    main()
