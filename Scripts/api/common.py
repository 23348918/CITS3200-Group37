from openai import OpenAI
from typing import Tuple, Optional
from anthropic import Anthropic
from pydantic import BaseModel

# Global Variables
chatgpt_client: OpenAI = None
gemini_client = None
claude_client = Anthropic = None
verbose: bool = False
auto: bool = False
custom_str: str = None
prompt: str = None

# Global Classes
class AnalysisResponse(BaseModel):
        description: str
        reasoning: str
        action: str

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
    "Also include if driver can change lane, overtake or turn left/right.\n\n"
    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
    "Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
    "Recommended Action: In few words, give suggestion as to what action should be taken by the driver. \n"
    "Reasoning: Explain in only one sentence the reason for recommended action. Only talk about what is specifically about the scene. Avoid generic driving safety advice.\n"
)

# TODO: Set up Logging (track response time, token count, errors etc.)

# TODO: Possibly a config class to allow for batch processing option here instead of CLI

# Global Functions
def append_prompt(custom_str: str = None) -> None:
    global prompt
    if custom_str is not None:
        prompt = PROMPT + custom_str
    else:
        prompt = PROMPT
    
def set_verbose(value: bool) -> None:
    global verbose
    verbose = value

def set_prompt(prompt: str) -> None:
    global PROMPT
    PROMPT = prompt
    if verbose:
        print(f"Custom Prompt: {prompt}")

def set_custom(string: str) -> None:
    global custom_str
    custom_str = string