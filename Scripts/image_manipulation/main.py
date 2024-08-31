import argparse
from PIL import Image
from filters import (
    darkness_filter, 
    brightness_filter, 
    gaussian_blur_filter, 
    intensity_filter, 
    motion_blur_filter
)

from overlay import (
    process_image_overlay,
    process_video_overlay
)

from typing import Callable, Dict, Tuple, Iterator
from pathlib import Path
import cv2
import numpy as np

FILTERS: Dict[str, Callable[[Image.Image, float], Image.Image]] = {
    "darkness": darkness_filter,
    "brightness": brightness_filter,
    "gaussian": gaussian_blur_filter,
    "intensity": intensity_filter,
    "motion": motion_blur_filter,
}

# Define overlay paths
OVERLAYS = {
    "rain": Path("Scripts/image_manipulation/overlay_images/rain.png"),
    "fog": Path("Scripts/image_manipulation/overlay_images/fog.png"),
    "graffiti": Path("Scripts/image_manipulation/overlay_images/graffiti.png"),
    "lens-flare": Path("Scripts/image_manipulation/overlay_images/lens_flare.png"),
    "wet-filter": Path("Scripts/image_manipulation/overlay_images/wet_filter.png")
}

IMAGE_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.heic', '.heif'
)

VIDEO_EXTENSIONS: Tuple[str, ...] = (
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for applying filters to an image.
    
    Returns:
        Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Apply filters or overlays to an image.")
    parser.add_argument("input_path",
                        type=str,
                        help="Path to the input directory."
    )
    parser.add_argument("effect",
                        type=str,
                        choices=list(FILTERS.keys()) + list(OVERLAYS.keys()),
                        help="Which filter or overlay will be applied to the image."
    )
    parser.add_argument("-s", "--strength",
                        type=float,
                        default=0.5,
                        help="If a filter is chosen, the strength of the filter from 0.0 to 1.0. Default is 0.5."
    )
    return parser.parse_args()  

def directory_iterator(directory: Path) -> Iterator[Path]:
    """Creates an iterator that yields valid files from a directory and its subdirectories.
    
    Args:
        directory: The directory path to iterate over.

    Yields:
        Paths to valid files.
    """
    for path in directory.rglob('*'):
        if path.suffix.lower() in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS:
            yield path

def process_image(file_path: Path, effect_name: str, strength: float) -> None:
    """Applies the given effect to an image and saves it in a folder called "Output".
    
    Args:
        file_path: Path to the input image file.
        effect_name: Name of the effect to apply.
        strength: Strength of the filter effect.
    """
    output_dir = Path("Output")
    output_dir.mkdir(exist_ok=True)  # Create output directory if it doesn't exist
    output_path = output_dir / f"{effect_name}_{file_path.name}"

    image: Image.Image = Image.open(file_path)

    if effect_name in FILTERS:
        filter_func: Callable[[Image.Image, float], Image.Image] = FILTERS[effect_name]
        image = filter_func(image, strength)
    elif effect_name in OVERLAYS:
        image = process_image_overlay(image, effect_name, OVERLAYS[effect_name])
    
    image.save(output_path)

def process_video(file_path: Path, effect_name: str, strength: float) -> None:
    """Applies the given effect to a video and saves it in a folder called 'Output'.

    Args:
        file_path: Path to the input video file.
        effect_name: Name of the effect to apply.
        strength: Strength of the filter effect.
    """
    cap = cv2.VideoCapture(str(file_path))
    if not cap.isOpened():
        print(f"Error opening video file {file_path}")
        return

    fps: int = int(cap.get(cv2.CAP_PROP_FPS))
    width: int = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height: int = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_dir = Path("Output")
    output_dir.mkdir(exist_ok=True)  # Create output directory if it doesn't exist
    output_path = output_dir / f"{effect_name}_{file_path.name}"

    fourcc: int = cv2.VideoWriter_fourcc(*'mp4v')
    out: cv2.VideoWriter = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    filter_func = FILTERS.get(effect_name)
    overlay_path = OVERLAYS.get(effect_name)

    ret: bool
    frame: np.ndarray
    ret, frame = cap.read()
    while ret:
        pil_image: Image.Image = Image.fromarray(frame)

        if filter_func:
            filtered_image: Image.Image = filter_func(pil_image, strength)
        elif overlay_path:
            filtered_image: Image.Image = process_image_overlay(pil_image, effect_name, overlay_path)
        else:
            raise ValueError(f"Unknown effect: {effect_name}")

        cv_image: np.ndarray = np.array(filtered_image)

        out.write(cv_image)
        ret, frame = cap.read()

    cap.release()
    out.release()


def main() -> None:
    """Main function to parse arguments, apply the selected filter to images or videos, and save the results."""
    args: argparse.Namespace = parse_arguments()
    input_path = Path(args.input_path)

    for file_path in directory_iterator(input_path):
        file_extension = file_path.suffix.lower()

        if file_extension in VIDEO_EXTENSIONS:
            process_video(file_path, args.effect, args.strength)
        elif file_extension in IMAGE_EXTENSIONS:
            process_image(file_path, args.effect, args.strength)


if __name__ == "__main__":
    main()
