import json
from openai import OpenAI
from typing import Tuple
from anthropic import Anthropic
from pydantic import BaseModel, create_model
from pathlib import Path

# Global Variables
chatgpt_client: OpenAI = None
claude_client: Anthropic = None
verbose: bool = False
custom_str: str = None

# Response Format
# class AnalysisResponse(BaseModel):
#     hazards: str
#     vehicles: str
#     signs: str
#     road: str
#     weather: str
#     risk_rating: str
#     action: str
#     reason: str
class AnalysisResponse(BaseModel):
    description: str
    reasoning: str
    action: str
    # speed: str

# Constants
WAITING_TIMER: int = 15  # Waiting timer in seconds

PROCESS_STATUS : list = ["in_progress", "finalizing", "validating"]

VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.heif',
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.x-flv', 
    '.mpg', '.webm', '.3gp'
)

VIDEO_EXTENSIONS: Tuple[str, ...] = (
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.x-flv', '.mpg', '.webm', '.3gp'
)



LLMS: list[str] = ["chatgpt", "gemini", "claude"]
MAX_THREAD_WORKERS: int = 10
MAX_OUTPUT_TOKENS_CLAUDE: int = 4096
MAX_OUTPUT_TOKENS_GEMINI: int = 400

# prompt : str = (
# """You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. The user will provide you with an image or images to analyze. Each section should be short (a few words). IMPORTANT! DO NOT RAMBLE OR PRODUCE LONG RESPONSES. DO NOT REPEAT YOURSELF. LIST AT MOST 3 THINGS. Produce the output as a json with this format:

# hazards: List any potential hazards such as people, animals, obstacles. Use one or two words for each and use None is there aren't any.
# vehicles: List the types of vehicles in the scene (e.g., cars, buses, motorcycles).
# signs: Include any road signs, traffic lights, or road markings (e.g., stop sign, speed limit, traffic light).
# road: Describe the road type (e.g., intersection, freeway, country road).
# weather: Describe the weather condition (e.g., clear, rainy, foggy). Only give one response.
# risk_rating: Provide a risk rating for the situation on a scale of 1-10 where 1 is perfectly safe and 10 is life threatening.
# action: Recommend the action the driver should take. Avoid statements that are too general such as "stay alert" or "remain catious" or "slow down". (eg: maintain speed, let pedestrians cross, prepare to turn left)
# reason: Briefly explain the reason for the recommended action."""
# )
prompt : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. Keep your response concise."
    "The user will provide you with an image or series of images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words, always giving a result in quotations. "
    "description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles."
    "reasoning: Explain in only one sentence the reason for recommended action. Only talk about what is specifically about the scene. Avoid generic driving safety advice."
    "action: In few words, give suggestion as to what action should be taken by the driver. Also include if driver can change lane, overtake or turn left/right. "
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
        custom_str = custom_str.replace('\n', ' ')
        prompt = prompt + '\n' + custom_str
    else:
        prompt = prompt

def set_verbose(value: bool = True) -> None:
    global verbose
    verbose = value
    verbose_print(f"Verbose: {value}")

def verbose_print(*args, **kwargs) -> None:
    if verbose:
        print(*args, **kwargs)

def set_custom(txt_file: str) -> None:
    global custom_str
    if txt_file is None:
        append_prompt()
        return
    file_path = Path(txt_file)
    if not file_path.suffix.lower() == '.txt':
        raise ValueError("The file must be of type .txt")
    try:
        with open(file_path, 'r') as file:
            custom_str = file.read()
            append_prompt(custom_str)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    customise_analysis_response(custom_str)

def customise_analysis_response(custom_str: str):
    """
    Dynamically modify the fields of the provided AnalysisResponse model
    by recreating and reassigning it with new fields.
    
    Args:
        custom_str : String containing custom field definitions.
    """
    if not custom_str:
        return

    # Collect dynamic fields from the input string
    dynamic_fields = {}
    lines = custom_str.splitlines()
    for line in lines:
        if ": " in line:
            first_word = line.split(": ")[0].strip()
            dynamic_fields[first_word.lower()] = (str, ...)  # Assuming all fields are strings

    # Dynamically recreate the AnalysisResponse model with the additional fields
    global AnalysisResponse
    AnalysisResponse = create_model(
        'AnalysisResponse',  # Keep the same name
        __base__=AnalysisResponse,  # Inherit the existing fields
        **dynamic_fields  # Add dynamic fields
    )
