import os
import sys
import argparse
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Tuple, Callable
from api import chatgpt_request, gemini_request, claude_request, llama_request
from common import verbose, client

VALID_EXTENSIONS: Tuple[str, ...] = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.heic', '.heif', 
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

LLMS: Dict[str, Callable[[], None]] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request,
    "llama": llama_request
}

def valid_files_dictionary(directory: str) -> Dict[str, List[str]]:
    """
    @brief Organizes valid files in a directory into a dictionary, with directory paths as keys and lists of file names as values.
    @params directory (str): The path to the directory to be processed.
    @return Dict[str, List[str]]: A dictionary where each key is a directory path and the value is a list of valid file names.
    """
    files_dictionary: Dict[str, List[str]] = {}
    
    for root, _, files in os.walk(directory):
        valid_files: List[str] = [f for f in files if f.endswith(VALID_EXTENSIONS)]
        if valid_files:
            files_dictionary[root] = valid_files
    
    return files_dictionary


def generate_processing_dictionary(args_path: str) -> Dict[str, List[str]]:
    """
    @brief Generates a dictionary of files to process based on whether the input path is a file or a directory.
    @params args_path (str): The path to the file or directory to be processed.
    @return Dict[str, List[str]]: A dictionary where each key is a directory path and the value is a list of file names, or a single file if the path is a file.
    """
    path: Path = Path(args_path)
    
    if path.is_file() and path.suffix in VALID_EXTENSIONS:
        return {str(path.parent): [path.name]}
    
    if path.is_dir():
        processing_dictionary: Dict[str, List[str]] = valid_files_dictionary(args_path)
        if not processing_dictionary:
            print(f"Directory '{path}' does not contain any valid files for processing. Please use {VALID_EXTENSIONS}.", file=sys.stderr)
            sys.exit(1)
        return processing_dictionary
    
    print(f"'{path.name}' is not a supported file type. Please use {VALID_EXTENSIONS}.", file=sys.stderr)
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """
    @brief Parses command-line arguments for running the simulation of an LLM model.
    @return argparse.Namespace: Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Runs a simulation of an LLM model with image or video files exporting them to a CSV file.")
    parser.add_argument("llm_model",
                        type=str,
                        choices=["chatgpt", "gemini", "claude", "llama"],
                        help="Name of desired LLM model to process image or video files"
    )
    parser.add_argument("input_path",
                        type=str,
                        help="Path to the input file or directory"
    )
    parser.add_argument("prompt",
                        type=str,
                        help="Prompt to give to the LLM for processing.",
                        default="You are an AI system designed to enhance road safety by accurately identifying potential hazards and providing timely warnings to drivers. Your task is to analyze the following scenarios and respond with appropriate safety recommendations.",
                        nargs="?"
    )
    parser.add_argument("--verbose",
                        action="store_true",
                        help="Enables verbose output."
    )
    return parser.parse_args()


def main() -> None:
    """
    @brief Main function to parse arguments, validate paths, generate processing dictionaries, and run the selected LLM model.
    @return None
    """
    args: argparse.Namespace = parse_arguments()

    if not os.path.exists(args.input_path):
        print(f"'{args.input_path}' is not a valid image or video path.", file=sys.stderr)
        sys.exit(1)

    processing_dictionary: Dict[str, List[str]] = generate_processing_dictionary(args.input_path)

    # TODO: Use Click or something for this instead
    if args.verbose:
        print(f"----------------------------------------")
        print(f"Verbose mode enabled")
        print(f"LLM model: {args.llm_model}")
        print(f"Input path: {args.input_path}")
        print(f"Prompt: {args.prompt}")
        print(f"----------------------------------------")
        print(f"Processing Dictionary: ")
        pprint(processing_dictionary)

    if args.llm_model not in LLMS:
        print(f"'{args.llm_model}' is not a valid model.", file=sys.stderr)
        sys.exit(1)

    # TODO: Process media in the chosen LLM and return JSON output  (Project requirement 5)
    LLMS[args.llm_model](processing_dictionary)

    # TODO: Process to spreadsheet                                  (Project requirement 6)
    


if __name__ == "__main__":
    main()
