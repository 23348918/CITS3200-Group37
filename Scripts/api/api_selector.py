from auth import authenticate
from request import analyse_image
from typing import Dict, List
import common as common
from utils import generate_csv_output

# def chatgpt_request(processing_directory: Dict[str, List[str]]) -> None:
#     # TODO: Currently only works for 1 image, allow for working with multiple and subdirectories
#     # Authenticate the key to ensure it can be used
#     common.client = authenticate("../../Private/ClientKeys/chatgpt-api.txt")

#     # Process media
#     for key in processing_directory:

#         for file in processing_directory[key]:
#             path_str: str = f"{key}/{file}"
            
#             if common.verbose:
#                 print(f"Sending {path_str} to chatgpt-4o-mini...")
#             result_dict: Dict[str, str] = analyse_image(path_str)
#             if common.verbose:
#                 print(f"Received result from chatgpt-4o-mini: {result_dict}")

#             # NOTE : changed function name to generate_csv_output
#             # Output to given file csv
#             generate_csv_output(result_dict)
#             if common.verbose:
#                 print("Media has been successfully exported to csv.")
#     pass

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