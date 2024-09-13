from auth import authenticate
from typing import Dict, List
from gpt_request import analyse_image
import common as common
from utils import generate_csv_output


def chatgpt_request(path_str: str) -> None:
    # TODO: Currently only works for 1 image, allow for working with multiple and subdirectories

    # Process media
    if common.verbose:
        print(f"Sending {path_str} to chatgpt-4o-mini...")

    result_dict: Dict[str, str] = analyse_image(path_str)
    
    if common.verbose:
        print(f"Received result from chatgpt-4o-mini: {result_dict}")
        
    # Output to given file csv
    generate_csv_output(result_dict)
    if common.verbose:
        print("Media has been successfully exported to csv.")
    pass


def gemini_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass


def claude_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass


def llama_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass