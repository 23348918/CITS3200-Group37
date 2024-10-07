from gpt_request import analyse_image as gpt_analyse_image, analyse_video as gpt_analyse_video
from claude_request import analyse_image as claude_analyse_image, analyse_video as claude_analyse_video
from gemini_request import analyse_image as gemini_analyse_image, analyse_video as gemini_analyse_video
from typing import Dict
from pathlib import Path
import common as common
from utils import generate_csv_output
import os


def chatgpt_request(process_path: Path) -> None:
    """
    Process a request to the ChatGPT API.

    Args:
        process_path: location of media to be processed by LLM
    """          
    if common.verbose:
        print(f"Sending {process_path} to chatgpt-4o-mini...")
    if process_path.suffix in common.VIDEO_EXTENSIONS:
        result_dict: Dict[str, str] = gpt_analyse_video(process_path)
    else:
        result_dict: Dict[str, str] = gpt_analyse_image(process_path)
    if common.verbose:
        print(f"Received result from chatgpt-4o-mini: {result_dict}")

    filename = process_path.name
    output_directory = Path("../../Output/")
    
    generate_csv_output(result_dict, "chatgpt-4o-mini", filename, output_directory)

    if common.verbose:
        print("Media has been successfully exported to CSV.")


def gemini_request(process_path: Path) -> None:
    """
    Process a request to the Gemini API.

    Args:
        process_path: location of media to be processed by LLM
    """
    if common.verbose:
        print(f"Sending {process_path} to gemini-1.5-pro...")
    if process_path.suffix in common.VIDEO_EXTENSIONS:
        result_dict: Dict[str, str] = gemini_analyse_video(process_path)
    else:
        result_dict: Dict[str, str] = gemini_analyse_image(process_path)
    if common.verbose:
        print(f"Received result from gemini-1.5-pro: {result_dict}")

    filename = process_path.name
    output_directory = Path("../../Output/")

    generate_csv_output([result_dict], "gemini-1.5-pro", filename, output_directory)
    if common.verbose:
        print("Media has been successfully exported to CSV.")


def claude_request(process_path: Path) -> None:
    """
    Process a request to the Claude API.

    Args:
        process_path: location of media to be processed by LLM
    """          
    result_dict = {"label": os.path.basename(process_path)}
    if common.verbose:
        print(f"Sending {process_path} to Claude-1...")

    if process_path.suffix in common.VIDEO_EXTENSIONS:
        response = claude_analyse_video(process_path)
    else:
        response = claude_analyse_image(process_path)
    
    # Update result_dict with the response content
    result_dict.update(response)
    
    if common.verbose:
        print(f"Received result from Claude-1: {result_dict}") 
    
    filename = process_path.name
    output_directory = Path("../../Output/")

    generate_csv_output(result_dict, "claude", filename, output_directory)
    
    if common.verbose:
        print("Media has been successfully exported to CSV.")
