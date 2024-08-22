import os
import sys
import argparse
from pathlib import Path
from pprint import pprint
from typing import Dict, List
from api import chatgpt_request, gemini_request, claude_request, llama_request


VALID_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.bmp', '.gif', 
    '.tiff', '.tif', '.webp', '.heic', '.heif', 
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'
)

LLMS = {
    "chatgpt" : chatgpt_request,
    "gemini" : gemini_request,
    "claude" : claude_request,
    "llama" : llama_request
}

"""
@brief Organises valid files in a directory into a dictionary, with directory paths as keys and lists of file names as values.
@params directory (str): The path to the directory to be processed.
@return Dict[str, List[str]]: A dictionary where each key is a directory path and the value is a list of valid file names.
"""
def valid_files_dictionary(directory: str) -> Dict[str, List[str]]:
    files_dictionary = {}
    
    for root, _, files in os.walk(directory):
        valid_files = [f for f in files if f.endswith(VALID_EXTENSIONS)]
        if valid_files:
            files_dictionary[root] = valid_files
    
    return files_dictionary

"""
@brief Generates a dictionary of files to process based on whether the input path is a file or a directory.
@params args_path (str): The path to the file or directory to be processed.
@return Dict[str, List[str]]: A dictionary where each key is a directory path and the value is a list of file names, or a single file if the path is a file.
"""
def generate_processing_dictionary(args_path: str) -> Dict[str, List[str]]:
    path = Path(args_path)
    
    if path.is_file() and path.suffix in VALID_EXTENSIONS:
        return {str(path.parent): [path.name]}
    
    if path.is_dir():
        processing_dictionary = valid_files_dictionary(args_path)
        if not processing_dictionary:
            print(f"Directory '{path}' does not contain any valid files for processing. Please use {VALID_EXTENSIONS}", file=sys.stderr)
            sys.exit(1)
        return processing_dictionary
    
    print(f"'{path.name}' is not a supported file type. Please use {VALID_EXTENSIONS}", file=sys.stderr)
    sys.exit(1)

"""
@brief Parses command-line arguments for running the simulation of an LLM model.
@return argparse.Namespace: Parsed command-line arguments.
"""
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runs a simulation of an LLM model with image or video files exporting them to a csv file")
    parser.add_argument('llm_model',
                        type=str,
                        choices=['chatgpt', 'gemini', 'claude', 'llama'],
                        help='Name of desired LLM model to process image or video files'
    )
    parser.add_argument('image_or_video_path',
                        type=str,
                        help='Path to the input image or video file. Supports directories and sub-directories'
    )
    parser.add_argument('prompt',
                        type=str,
                        help='Prompt to give to the LLM for processing',
                        default = "You are an AI system designed to enhance road safety by accurately identifying potential hazards and providing timely warnings to drivers. Your task is to analyze the following scenarios and respond with appropriate safety recommendations.",
                        nargs='?'
    )
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Enables verbose output'
    )
    return parser.parse_args()

"""
@brief Main function to parse arguments, validate paths, generate processing dictionaries, and run the selected LLM model.
"""
def main() -> None:
    args = parse_arguments()

    if not os.path.exists(args.image_or_video_path):
        print(f"'{args.image_or_video_path}' is not a valid image or video path.", file=sys.stderr)
        sys.exit(1)

    processing_dictionary = generate_processing_dictionary(args.image_or_video_path)

    # TODO: Use Click or something for this instead
    if args.verbose:
        print(f"----------------------------------------")
        print(f"Verbose mode enabled")
        print(f"LLM model: {args.llm_model}")
        print(f"Input path: {args.image_or_video_path}")
        print(f"Prompt: {args.prompt}")
        print(f"----------------------------------------")
        print(f"Processing Dictionary: ")
        pprint(processing_dictionary)


    if not args.llm_model in LLMS:
        print(f"'{args.llm_model}' is not a valid model.", file=sys.stderr)
        sys.exit(1)
        
    if args.verbose:
        print(f"Sending to {args.llm_model}")

    LLMS[args.llm_model]()

    # TODO: Process media in the chosen LLM and return JSON output  (Project requirement 5)

    # TODO: Process to spreadsheet                                  (Project requirement 6)


if __name__ == "__main__":
    main()
