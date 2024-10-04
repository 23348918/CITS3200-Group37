import common
from common import verbose_print
import sys
from pathlib import Path
from requests import chatgpt_request, gemini_request, claude_request
from utils import generate_csv_output
from typing import Callable, Any

REQUEST_FUNCTIONS: dict[str, Callable] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request
}


def process_model(model_name: str, file_path_str: str, auto: bool):
    verbose_print(f"Processing model: {common.model_name}")
    if common.model_name not in common.LLMS:
        print("Invalid model name")
        sys.exit(1)
    file_path: Path = Path(file_path_str)
    if file_path.is_file() and file_path.suffix in common.VALID_EXTENSIONS:
        verbose_print(f"Sending {file_path} to {model_name}...")
        is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
        request_output: list[dict[str, Any]] = REQUEST_FUNCTIONS[model_name](model_name, file_path, is_video)
    elif file_path.is_dir():
        pass
    else:
        print(f"{file_path} is not a valid file or directory.")
        sys.exit(1)
    
    generate_csv_output(request_output, model_name)

def check_model(): 
    pass

def export_model():
    pass

def list_models():
    pass