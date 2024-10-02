from gpt_request import analyse_image as gpt_analyse_image, analyse_video as gpt_analyse_video
from claude_request import analyse_image as claude_analyse_image, analyse_video as claude_analyse_video
from typing import Dict
from pathlib import Path
import common as common
from utils import generate_csv_output, save_results_to_json, json_to_dict


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

    generate_csv_output(result_dict, "gpt")
    if common.verbose:
        print("Media has been successfully exported to CSV.")
    pass


def gemini_request(process_path: Path) -> None:
    """
    Process a request to the Gemini API.

    Args:
        process_path: location of media to be processed by LLM
    """
    print("DONE")
    pass


def claude_request(process_path: Path) -> None:
    """
    Process a request to the Claude API.

    Args:
        process_path: location of media to be processed by LLM
    """          
    if common.verbose:
        print(f"Sending {process_path} to Claude-1...")
    if process_path.suffix in common.VIDEO_EXTENSIONS:
        result_dict: Dict[str, str] = claude_analyse_video(process_path)
    else:
        result_dict: Dict[str, str] = claude_analyse_image(process_path)
    if common.verbose:
        print(f"Received result from Claude-1: {result_dict}")

    output_file = Path("../../Output/output_results.json")
    save_results_to_json(result_dict, output_file)
    result_dict = json_to_dict(output_file)

    generate_csv_output(result_dict, "claude")
    if common.verbose:
        print("Media has been successfully exported to CSV.")
    pass


def llama_request(process_path: Path) -> None:
    """
    Process a request to the LLaMA API.

    Args:
        process_path: location of media to be processed by LLM
    """
    print("DONE")
    pass
