from auth import authenticate
from request import analyse_image, analyse_video
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
    # TODO: Currently only works for 1 image, allow for working with multiple and subdirectories

    # Process media
    if common.verbose:
        print(f"Sending {process_path} to chatgpt-4o-mini...")

        # NOTE : change the path_string to use / instead of \ as mac and linux only takes /
        for file in processing_directory[key]:
            path_str: str = f"{key}/{file}"
            
            if common.verbose:
                print(f"Sending {path_str} to chatgpt-4o-mini...")
            if file.endswith(common.VIDEO_EXTENSIONS):
                result_dict: Dict[str, str] = analyse_video(path_str)
            else:
                result_dict: Dict[str, str] = analyse_image(path_str)
            if common.verbose:
                print(f"Received result from chatgpt-4o-mini: {result_dict}")

            # NOTE : changed function name to generate_csv_output
            # Output to given file csv
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