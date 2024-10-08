import json
from openai import OpenAI
from typing import Tuple, Optional
from anthropic import Anthropic
from pydantic import BaseModel
from pathlib import Path

# Global Variables
chatgpt_client: OpenAI = None
claude_client: Anthropic = None
verbose: bool = False
custom_str: str = None
prompt: str = None

# Response Format
class AnalysisResponse(BaseModel):
    description: str
    reasoning: str
    action: str

# Constants
WAITING_TIMER: int = 2  # Waiting timer in seconds

PROCESS_STATUS : list = ["completed", "failed", "cancelled", "expired"]

VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif',
    '.tiff', '.tif', '.webp', '.heic', '.heif',
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

IMAGE_EXTENSIONS: Tuple[str, ...] = (
    ".png", ".jpeg", ".jpg", ".gif", ".webp"
)

VIDEO_EXTENSIONS: Tuple[str, ...] = (
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

IMAGE_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.webp'
)

LLMS: list[str] = ["chatgpt", "gemini", "claude"]
MAX_THREAD_WORKERS: int = 10
MAX_OUTPUT_TOKENS: int = 100

PROMPT : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. Keep your response concise."
    "The user will provide you with an image or series of images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words:"
    "1. description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles."
    "3. reasoning: Explain in only one sentence the reason for recommended action. Only talk about what is specifically about the scene. Avoid generic driving safety advice."
    "2. action: In few words, give suggestion as to what action should be taken by the driver. "
    "Also include if driver can change lane, overtake or turn left/right."
)

USER_PROMPT: json = {
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": "Analyze the following image and provide json output."
        }
    ]
}

ARG_INFO = [
    # Positional argument for LLM model
    {
        "name": "llm_model",
        "nargs": "?",
        "type": str,
        "choices": ["chatgpt", "gemini", "claude"],
        "help": "Name of the LLM model to process image or video files. Required for process, check, and export."
    },

    # Mutually exclusive group for process and batch operations
    {
        "group": "exclusive",
        "flags": ["-p", "--process"],
        "metavar": "FILE_PATH",
        "help": "Process the input file or directory."
    },
    {
        "group": "exclusive",
        "flags": ["-b", "--batch"],
        "metavar": "FILE_PATH",
        "help": "Process the input file or directory with batch processing."
    },
    {
        "group": "exclusive",
        "flags": ["-l", "--list"],
        "action": "store_true",
        "help": "List all batches."
    },
    {
        "group": "exclusive",
        "flags": ["-ch", "--check"],
        "metavar": "BATCH_ID",
        "help": "Check the status of a batch."
    },
    {
        "group": "exclusive",
        "flags": ["-e", "--export"],
        "metavar": "BATCH_ID",
        "help": "Export the results of a batch."
    },
    # General arguments (verbose is first)
    {
        "flags": ["-v", "--verbose"],
        "action": "store_true",
        "help": "Enable verbose output."
    },
    {
        "flags": ["--prompt"],
        "metavar": "PROMPT",
        "help": "Prompt selector for the processing mode. Optional for --process."
    },  
    {
        "flags": ["-a", "--auto"],
        "action": "store_true",
        "help": "Fully automated processing mode, from input to export of batch processing."
    },  
    {
        "flags": ["-c", "--custom"],
        "metavar": "TXT-PATH",
        "help": "Allows addition of custom prompts via a txt file path."
    }, 
]

# Global Functions
def append_prompt(custom_str: str = None) -> None:
    global prompt
    if custom_str is not None:
        prompt = PROMPT + custom_str
    else:
        prompt = PROMPT

def set_verbose(value: bool = True) -> None:
    global verbose
    verbose = value
    verbose_print(f"Verbose: {value}")

def set_prompt(prompt: str) -> None:
    global PROMPT
    PROMPT = prompt
    verbose_print(f"Custom Prompt: {prompt}")

def verbose_print(*args, **kwargs) -> None:
    if verbose:
        print(*args, **kwargs)

def set_custom(custom: str) -> None:
    global custom_str
    file_path = Path(custom)
    if not file_path.lower().endswith('.txt'):
        raise ValueError("The file must be of type .txt")

    with open(file_path, 'r') as file:
        custom_str = file.read()
        append_prompt(custom_str)