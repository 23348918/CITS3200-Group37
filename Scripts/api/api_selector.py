from auth import authenticate
from gpt_request import analyse_image, analyse_video
from typing import Dict, List
from pathlib import Path
from gpt_request import analyse_image
import common as common
from utils import generate_csv_output


def chatgpt_request(process_path: Path) -> None:
    """
    Process a request to the chatgpt API

    Args:
        process_path: location of media to be processed by LLM
    """          
    if common.verbose:
        print(f"Sending {process_path} to chatgpt-4o-mini...")
    if process_path.suffix in common.VIDEO_EXTENSIONS:
        result_dict: Dict[str, str] = analyse_video(process_path)
    else:
        result_dict: Dict[str, str] = analyse_image(process_path)
    if common.verbose:
        print(f"Received result from chatgpt-4o-mini: {result_dict}")

    generate_csv_output(result_dict)
    if common.verbose:
        print("Media has been successfully exported to csv.")
    pass


def gemini_request(process_path: Path) -> None:
    """
    Process a request to the gemini API

    Args:
        process_path: location of media to be processed by LLM
    """
    print("DONE")
    pass


def claude_request(process_path: Path) -> None:
    """
    Process a request to the claude API

    Args:
        process_path: location of media to be processed by LLM
    """
    print("DONE")
    pass


def llama_request(process_path: Path) -> None:
    """
    Process a request to the llama API

    Args:
        process_path: location of media to be processed by LLM
    """
    print("DONE")
    pass