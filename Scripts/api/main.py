import argparse
import os
import sys
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Tuple, Callable
from api_selector import chatgpt_request, gemini_request, claude_request, llama_request
from common import VALID_EXTENSIONS, PROMPT, set_verbose

LLMS: Dict[str, Callable[[], None]] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request,
    "llama": llama_request
}

def valid_files_dictionary(directory: str) -> Dict[str, List[str]]:
    """Organises valid files in a directory into a dictionary.
    
    Args:
        directory: Path to the directory to be processed.
    
    Returns:
        A dictionary with directory paths as keys and lists of valid file names as values.
    """
    files_dictionary: Dict[str, List[str]] = {}
    
    for root, _, files in os.walk(directory):
        valid_files: List[str] = [file for file in files if file.endswith(VALID_EXTENSIONS)]
        if valid_files:
            files_dictionary[root] = valid_files
    
    return files_dictionary

 # Code Review NOTE TODO : 
 # I think it would be better to just recursivly call this function 
 # ifdir -> go into that path for item in that path, if isfile() add to dict, else recusive call the func.
 # The proces of the function valid_files_dictionary (above) is similar to if path.isfile()
 # with little modification we can do this recursively.
 
def generate_processing_dictionary(path_str: str) -> Dict[str, List[str]]:
    """Generates a dictionary of files to process based on whether the input path is a file or a directory.
    
    Args:
        path_str: The path to the file or directory to be processed.
    
    Returns:
        A dictionary with directory paths as keys and lists of file names as values,
        or a single file if the path is a file.
    
    Raises:
        SystemExit: If the path is invalid or does not contain valid files.
    """
    path: Path = Path(path_str)
    
    if path.is_file() and path.suffix in VALID_EXTENSIONS:
        return {str(path.parent): [path.name]}
    
    if path.is_dir():
        processing_dictionary: Dict[str, List[str]] = valid_files_dictionary(path_str)
        if not processing_dictionary:
            print(f"Directory '{path}' does not contain any valid files for processing. Please use {VALID_EXTENSIONS}.", file=sys.stderr)
            sys.exit(1)
        return processing_dictionary
    
    print(f"'{path_str}' is not a supported file type. Please use {VALID_EXTENSIONS}.", file=sys.stderr)
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for running the simulation of an LLM model.
    
    Returns:
        Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Runs a simulation of an LLM model with image or video files, exporting results to a CSV file."
    )
    parser.add_argument(
        "llm_model",
        type=str,
        choices=["chatgpt", "gemini", "claude", "llama"],
        help="Name of the LLM model to process image or video files"
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to the input file or directory"
    )
    parser.add_argument(
        "prompt",
        type=str,
        help="Prompt for the LLM for processing.",
        default=PROMPT,
        nargs="?"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enables verbose output."
    )
    return parser.parse_args()


def main() -> None:
    """Main function to parse arguments, validate paths, generate processing dictionaries, and run the selected LLM model."""
    args: argparse.Namespace = parse_arguments()

    if not os.path.exists(args.input_path):
        print(f"'{args.input_path}' is not a valid image or video path.", file=sys.stderr)
        sys.exit(1)
        
        
    processing_dictionary: Dict[str, List[str]] = generate_processing_dictionary(args.input_path)

    if args.verbose:
        set_verbose(True)
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
