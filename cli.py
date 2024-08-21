import os
import sys
import argparse
from pathlib import Path
from pprint import pprint

# TODO: Check if these are supported by all LLMs
#  Acceptable extensions for chosen LLM models
valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')

def valid_files_dictionary(directory: str) -> dict[str, list[str]]:
    """
    @brief Organises each valid file to be stored in a dictionary with the key being the subdirectory location

    @param directory: directory to be turned into dictionary
    @type directory: str
    @return: dictionary of all valid files for processing
    @rtype: dict
    """

    files_dictionary = {}
    
    # Loop over given directory
    with os.scandir(directory) as files:

        # Loop over each file in directory
        for file in files:
            
            # Recursively call function if subdirectory is found and add to processing dictionary
            if file.is_dir():
                subdir_files = valid_files_dictionary(file.path)
                files_dictionary.update(subdir_files)

            elif file.is_file() and file.name.endswith(valid_extensions):

                # Add directory to dictionary if doesn't already exist
                if directory not in files_dictionary:
                    files_dictionary[directory] = []

                # Add to dictionary
                files_dictionary[directory].append(file.name)
    
    return files_dictionary


def main():
    """
    @brief Acts as the command line interface for the red teaming LLM program.

    """
    
    # Create parser with description
    parser = argparse.ArgumentParser(description="Runs a simulation of an LLM model with image or video files exporting them to a csv file")

    # Add parser for LLM model, image or video path (supports sub-directories), custom prompt and verbose
    parser.add_argument('llm_model',
                        type=str,
                        choices=['chatgpt', 'gemini', 'claude', 'llama'],
                        help='Name of desired LLM model to process image or video files'
    )
    parser.add_argument('image_or_video_path',
                        type=str,
                        help='Path to the input image or video file. Supports folders and sub-folders'
    )
    parser.add_argument('prompt',
                        type=str,
                        help='Prompt to give to the LLM for processing',
                        default = "You are an AI system designed to enhance road safety by accurately identifying potential hazards and providing timely warnings to drivers. Your task is to analyze the following scenarios and respond with appropriate safety recommendations.",
                        nargs='?'
    )
    parser.add_argument('--verbose',
                        action='store_true',
                        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Check for valid path and check either 
    if not os.path.exists(args.image_or_video_path):
        print(f"'{args.image_or_video_path}' is not a valid image or video path.", file=sys.stderr)
        sys.exit(1)

    path = Path(args.image_or_video_path)

    # Dictionary to send for processing images
    processing_dictionary = {}

    if path.is_file() and args.image_or_video_path.endswith(valid_extensions):
        path_split = args.image_or_video_path.split("\\")

        dir_part = '\\'.join(path_split[:-1])
        file_part = path_split[-1]

        processing_dictionary[dir_part] = [file_part]

    elif path.is_dir():
        # Create dictionary to store valid file images and paths
        processing_dictionary = valid_files_dictionary(args.image_or_video_path)

    # Not a valid file
    else:
        print(f"'{path.name}' is not a supported file type. Please use {valid_extensions}", file=sys.stderr)
        sys.exit(1)

    # Verbose output
    if args.verbose:
        print(f"----------------------------------------")
        print(f"Verbose mode enabled")
        print(f"LLM model: {args.llm_model}")
        print(f"Input path: {args.image_or_video_path}")
        print(f"Prompt: {args.prompt}")
        print(f"----------------------------------------")
        print(f"Processing Dictionary: ")
        pprint(processing_dictionary)

    # TODO: Alter images or videos to be processed to the LLM (Project requirement 4)
    if args.llm_model == 'chatgpt':
        if args.verbose:
            print(f"Sending to chatgpt")

            # TODO: Send to chatgpt

    elif args.llm_model == 'gemini':
        if args.verbose:
            print(f"Sending to gemini")

            # TODO: Send to gemini

    elif args.llm_model == 'claude':
        if args.verbose:
            print(f"Sending to claude")

            # TODO: Send to claude

    elif args.llm_model == 'llama':
        if args.verbose:
            print(f"Sending to llama")

            # TODO: Send to llama

    # TODO: Process media in the chosen LLM and return JSON output  (Project requirement 5)

    # TODO: Process to spreadsheet                                  (Project requirement 6)


if __name__ == "__main__":
    main()
