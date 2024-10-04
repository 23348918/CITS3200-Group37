from openai import OpenAI
from typing import Tuple
from anthropic import Anthropic
from pydantic import BaseModel

# Global Variables
chatgpt_client: OpenAI = None
gemini_client = None
claude_client: Anthropic = None
verbose: bool = False
model_name: str = None

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

LLMS: list[str] = ["chatgpt", "gemini", "claude"]

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

class AnalysisResponse(BaseModel):
    description: str
    reasoning: str
    action: str

# Global Functions
def set_verbose(value: bool = True) -> None:
    global verbose
    verbose = value
    verbose_print(f"Verbose: {value}")

def set_prompt(prompt: str) -> None:
    global PROMPT
    PROMPT = prompt
    verbose_print(f"Custom Prompt: {prompt}")

def set_model(model: str) -> None:
    global model_name
    model_name = model
    verbose_print(f"Model: {model_name}")

# common_args.py

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
        "flags": ["-l", "--list"],
        "action": "store_true",
        "help": "List all batches."
    },
    {
        "group": "exclusive",
        "flags": ["-c", "--check"],
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
]


def verbose_print(*args, **kwargs) -> None:
    if verbose:
        print(*args, **kwargs)