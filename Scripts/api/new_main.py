import argparse
import os
import sys
from auth import authenticate
from batch_operations import upload_batch_file, create_batch_file, list_batches, check_batch_process, export_batch_result
from utils import ask_save_location
from openai import OpenAI
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Tuple, Callable
from api_selector import chatgpt_request, gemini_request, claude_request, llama_request
from create_batch import get_file_paths, generate_batch_file
import common as common

LLMS: Dict[str, Callable[[], None]] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request,
    "llama": llama_request
}

def is_valid_file(file_path: str, valid_extensions: list) -> bool:
    """Check if the file has a valid extension."""
    return os.path.isfile(file_path) and file_path.lower().endswith(tuple(valid_extensions))

def is_valid_directory(dir_path: str) -> bool:
    """Check if the path is a valid directory."""
    return os.path.isdir(dir_path)

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for LLM model processing and batch operations."""

    parser = argparse.ArgumentParser(
        description="CLI for LLM model processing and batch operations."
    )

    # Mutually exclusive group to handle different modes (processing and batch operations)
    group = parser.add_mutually_exclusive_group(required=True)

    # Process operation
    group.add_argument(
        "-process",
        metavar="FILE_PATH",
        help="Process the input file or directory."
    )

    # Batch operations
    group.add_argument("-list", action="store_true", help="List all batches.")
    group.add_argument("-check", metavar="BATCH_ID", help="Check the status of a batch.")
    group.add_argument("-export", metavar="BATCH_ID", help="Export the results of a batch.")

    # Verbose flag
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output."
    )

    # LLM model only required for process, check, and export (not for list)
    parser.add_argument(
        "llm_model",
        type=str,
        nargs="?",
        choices=["chatgpt", "gemini", "claude", "llama"],
        help="Name of the LLM model to process image or video files. Required for process, check, and export."
    )

    args = parser.parse_args()

    # Ensure llm_model is required if not listing batches
    if not args.list and args.llm_model is None:
        parser.error("llm_model is required for processing, checking, or exporting.")

    return args

def main() -> None:
    """Main function to parse arguments, validate paths, generate processing dictionaries, and run the selected LLM model."""
    args: argparse.Namespace = parse_arguments()

    # TODO: Authenticate keys for all 3 models, program should run if the desired model key is in place.

    # Authenticate chatgpt client key
    common.chatgpt_client = authenticate("../../Private/ClientKeys/chatgpt-api.txt")

    # TODO: Authenticate gemini client key

    # TODO: Authenticate claude client key

    if args.verbose:
        print("Verbose mode enabled.")
    
    # Case 1: User would like to process image or directory
    
    # TODO: Implement video processing functionality here
    if args.process:

        process_path = args.process

        if args.verbose:
            print(f"Processing model: {args.llm_model}, input path: {args.process}")

        # Check path is valid
        if not os.path.exists(process_path):
            print(f"Cannot find path: '{process_path}'", file=sys.stderr)
            sys.exit(1)

        # Check valid LLM model
        if args.llm_model not in LLMS:
            print(f"'{args.llm_model}' is not a valid model.", file=sys.stderr)
            sys.exit(1)

        # Process singular image or video
        if is_valid_file(process_path, common.VALID_EXTENSIONS):
            LLMS[args.llm_model](process_path)

        # Batch process image or video directory
        elif is_valid_directory(process_path):
            if args.verbose:
                print(f"Creating batch process for input path: {args.process}")


            dirpath = get_file_paths(process_path)

            outpath = ask_save_location("batchfile.jsonl")
            generate_batch_file(dirpath, outpath)

            upload_batch = upload_batch_file(common.chatgpt_client, outpath)
            batch_object = create_batch_file(common.chatgpt_client, upload_batch)
            print(f"Batch created with ID: {batch_object.id}")
            

        # Invalid file type
        else:
            print(f"The path {process_path} is not a valid file, directory or zip file.")
            sys.exit(1)
        

        # If a valid image, we process via normal route, else we batch process.

        # if batch:
        #     upload_batch = upload_batch_file(chatgpt_client, args.process_batch)
        #     batch_object = create_batch_file(chatgpt_client, upload_batch)
        #     print(f"Batch created with ID: {batch_object.id}")


    # Case 2: User would like to list out all batches processing or processed.
    elif args.list:
        if args.verbose:
            print("Listing all batches.")
        
        # Lists all batches for Chatgpt
        print("Chatgpt:")
        list_batches(common.chatgpt_client)

        # TODO: List all batches for Gemini

        # TODO: List all batches for Claude

    # Case 3: User would like to check the progress of a given batch_id
    elif args.check:
        if args.verbose:
            print(f"Checking batch {args.check} for model: {args.llm_model}")
        
        if args.llm_model == "chatgpt":
            status = check_batch_process(common.chatgpt_client, args.check)
            print(status)

    # Case 4: User would like to export a completed batch
    elif args.export:
        if args.verbose:
            print(f"Exporting batch {args.export} for model: {args.llm_model}")
        
        location = ask_save_location("batchResult.json")
        print(location)

        # TODO: Instead of exporting go straight to csv (DO WE STORE THE RESULT??)
        export_batch_result(common.chatgpt_client, args.export, location)

if __name__ == "__main__":
    main()

