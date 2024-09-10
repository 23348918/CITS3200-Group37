from openai import OpenAI
from typing import Tuple


# Global Variables
client: OpenAI = None
verbose: bool = False

# Constants
VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif',
    '.tiff', '.tif', '.webp', '.heic', '.heif',
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

PROMPT : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. "
    "The user will provide you with an image or images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
    "1. Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
    "2. Recommended Action: In few words, give suggestion as to what action should be taken by the driver. "
    "Also include if driver can change lane, overtake or turn left/right.\n"
    "3. Reason: Explain in few words the reason for recommended action.\n\n"
)

# TODO: Set up Logging

# TODO: Possibly a config class to allow for batch processing option here instead of CLI

# Global Functions
def set_verbose(value: bool) -> None:
    global verbose
    verbose = value