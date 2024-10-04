from openai import OpenAI
from typing import Tuple
from anthropic import Anthropic
from pydantic import BaseModel

# Global Variables
chatgpt_client: OpenAI = None
gemini_client = None
claude_client = Anthropic = None
verbose: bool = False
auto: bool = False
is_custom: bool = False

# Global Classes
class AnalysisResponse(BaseModel):
        description: str
        reasoning: str
        action: str

class CustomAnalysisResponse(AnalysisResponse):
        custom_1: None
        custom_2: None
        custom_3: None

PROCESS_STATUS : list = ["completed", "failed",  " cancelled", "expired"]
WAITING_TIMER: int = 2  # Waiting timer in seconds

# Constants
VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif',
    '.tiff', '.tif', '.webp', '.heic', '.heif',
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

VIDEO_EXTENSIONS: Tuple[str, ...] = (
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

PROMPT : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. Keep your response concise."
    "The user will provide you with an image or series of images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
    "1. Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
    "3. Reasoning: Explain in only one sentence the reason for recommended action. Only talk about what is specifically about the scene. Avoid generic driving safety advice.\n"
    "2. Recommended Action: In few words, give suggestion as to what action should be taken by the driver. "
    "Also include if driver can change lane, overtake or turn left/right.\n\n"
)

# TODO: Set up Logging (track response time, token count, errors etc.)

# TODO: Possibly a config class to allow for batch processing option here instead of CLI

# Global Functions
def set_verbose(value: bool) -> None:
    global verbose
    verbose = value

def set_prompt(prompt: str) -> None:
    global PROMPT
    PROMPT = prompt
    if verbose:
        print(f"Custom Prompt: {prompt}")

def set_custom(value: bool) -> None:
    global is_custom
    is_custom = value