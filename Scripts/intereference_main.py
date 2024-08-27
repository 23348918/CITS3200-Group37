import argparse
from PIL import Image
from filters import darkness_filter, brightness_filter, gaussian_blur_filter, intensity_filter, motion_blur_filter
from typing import Callable, Dict, Tuple, Iterator
import os
import cv2
import numpy as np

FILTERS: Dict[str, Callable[[Image.Image, float], Image.Image]] = {
    "darkness": darkness_filter,
    "brightness": brightness_filter,
    "gaussian": gaussian_blur_filter,
    "intensity": intensity_filter,
    "motion": motion_blur_filter,
}

IMAGE_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.heic', '.heif'
)

VIDEO_EXTENSIONS: Tuple[str, ...] = (
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
            if file.lower().endswith(IMAGE_EXTENSIONS+VIDEO_EXTENSIONS):
                yield (root, file)


def process_image(file_path: str, filter_name: str, strength: float) -> None:
    """
    @brief Applies given filter to image and save it in folder called "Output"
    @return None
    """
    image: Image.Image = Image.open(file_path)
    filter_func: Callable[[Image.Image, float], Image.Image] = FILTERS.get(filter_name)
    if not filter_func:
        raise ValueError(f"Unknown filter: {filter_name}")

    image = filter_func(image, strength)
    output_path = f"Output/{filter_name}_{os.path.basename(file_path)}"
    image.save(output_path)


def process_video(file_path: str, filter_name: str, strength: float) -> None:
    """
    @brief Applies given filter to video and save it in folder called "Output"
    @return None
    """
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        print(f"Error opening video file {file_path}")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create VideoWriter object
    output_path = f"Output/{filter_name}_{os.path.basename(file_path)}"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    filter_func: Callable[[Image.Image, float], Image.Image] = FILTERS.get(filter_name)
    if not filter_func:
        raise ValueError(f"Unknown filter: {filter_name}")

    # Continues frame by frame until it is finished
    ret, frame = cap.read()
    while ret:
        # Filters done as a pillow image but video is done with cv2 so need to convert between them
        pil_image = Image.fromarray(frame)
        filtered_image = filter_func(pil_image, strength)
        cv_image = np.array(filtered_image)

        out.write(cv_image)
        ret, frame = cap.read()

    cap.release()
    out.release()

def main() -> None:
    """
    @brief Main function to parse arguments, apply the selected filter to the image, and save the result.
    @return None
    """
    args: argparse.Namespace = parse_arguments()

    for dir_path, file_name in directory_iterator(args.input_path):
        file_path = os.path.join(dir_path, file_name)
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension in VIDEO_EXTENSIONS:
            process_video(file_path, args.filter, args.strength)
        elif file_extension in IMAGE_EXTENSIONS:
            process_image(file_path, args.filter, args.strength)

if __name__ == "__main__":
    main()
