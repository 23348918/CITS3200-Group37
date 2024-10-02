import argparse
import os
import sys
from auth import authenticate
from gpt_batch_operations import upload_batch_file, create_batch_file, list_batches, check_batch_process, export_batch_result
from utils import get_save_path
from pathlib import Path
from typing import Dict, List, Callable
from api_selector import chatgpt_request, gemini_request, claude_request, llama_request
from create_batch import get_file_paths, generate_batch_file
import common as common
from claude_multi_request import parallel_process, get_file_dict
from pathlib import Path

LLMS: Dict[str, Callable[[], None]] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request,
    "llama": llama_request
}

def is_valid_file(file_path: Path, valid_extensions: list) -> bool:
    """Check if the file has a valid extension.

    Args:
        file_path: Path to the input media
        valid_extensions: list of valid extensions

    Returns:
        Boolean giving file validity.
    """
    # return os.path.isfile(file_path) and file_path.lower().endswith(tuple(valid_extensions))
    valid_extensions = tuple(valid_extensions)
    return file_path.is_file() and file_path.suffix.lower() in valid_extensions

def is_valid_directory(dir_path: str) -> bool:
    """Check if the given path is a valid directory.

    Args:
        dir_path: Path to the input media directory.

    Returns:
        Boolean value for valid directory.
    """
    return os.path.isdir(dir_path)

def batch_process(process_path: Path, llm_model: str) -> None:
    """Process a given directory and save as a batch file to send to LLM.

    Args:
        process_path: Path for the directory to be processed.
    """
    if common.verbose:
        print(f"Creating batch process for input path: {process_path}")
        
    dirpath: List[Path] = get_file_paths(process_path)
    filename = process_path.stem
    directory: Path = Path("../../Batch_Files")

    outpath = get_save_path(filename, directory)

    if common.verbose:
        print(f"File saved to Batch_Files as: {filename}.json")

    generate_batch_file(dirpath, outpath)

    upload_batch = upload_batch_file(common.chatgpt_client, outpath)
    batch_object = create_batch_file(common.chatgpt_client, upload_batch)
    print(f"Batch created with ID: {batch_object.id}")

def process(process_path: str, llm_model: str) -> None:
    """Process the given path as a singular or batch request
    
    Args:
        process_path: Path of file or directory to be processed by LLM
        llm_model: Chosen LLM model
    """
    if not os.path.exists(process_path):
            print(f"Cannot find path: '{process_path}'", file=sys.stderr)
            sys.exit(1)
    if llm_model not in LLMS:
        print(f"'{llm_model}' is not a valid model.", file=sys.stderr)
        sys.exit(1)

    # Process singular image or video
    if is_valid_file(process_path, common.VALID_EXTENSIONS):
        LLMS[llm_model](process_path)

    # Batch process image or video directory
    elif is_valid_directory(process_path):
        if llm_model == "chatgpt":
            batch_process(process_path, llm_model)
        elif llm_model == "claude":
            file_dict = get_file_dict(process_path)
            results = parallel_process(file_dict)
            for result in results:
                print(result)
    else:
        print(f"The path {process_path} is not a valid file, directory or zip file.")
        sys.exit(1)

def batches_list() -> None:
    """List a history of all batches for every model"""

    if common.verbose:
        print("Listing all batches.")
        
    # Lists all batches for Chatgpt
    print("Chatgpt:")
    list_batches(common.chatgpt_client)
    # TODO: List all batches for Gemini & Claude
    print("Gemini:")

    print("Claude:")

def check_batch(batch_id: str, llm_model: str) -> None:
    """Check the batch for the given batch id and llm model
    
    Args:
        batch_id: Batch id to check
        llm_model: The model the batch is from
    """
    if common.verbose:
        print(f"Checking batch {batch_id} for model: {llm_model}")
        
    if llm_model == "chatgpt":
        status = check_batch_process(common.chatgpt_client, batch_id)
        print(status)

def export_batch(batch_id: str, llm_model: str) -> None:
    """Export the batch for the given batch id and llm model
    
    Args:
        batch_id: Batch id to check
        llm_model: The model the batch is from
    """

    if common.verbose:
            print(f"Exporting batch {batch_id} for model: {llm_model}")
          
    filename: str = batch_id
    directory: Path = Path("../../Output")
    location = get_save_path(filename, directory)

    # TODO: Store to CSV instead
    export_batch_result(common.chatgpt_client, batch_id, location)
    
def parse_arguments() -> argparse.Namespace:
    """Parse the arguments from the command line

    Returns:
        Argsparse namespace
    """

    parser = argparse.ArgumentParser(
        description="CLI for LLM models processing and batch operations."
    )

    # Adds exclusivity to handle processing and batch operations
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

    # LLM model (not used for list)
    parser.add_argument(
        "llm_model",
        type=str,
        nargs="?",
        choices=["chatgpt", "gemini", "claude", "llama"],
        help="Name of the LLM model to process image or video files. Required for process, check, and export."
    )

    # Prompt selector
    parser.add_argument(
        "--prompt",
        metavar="PROMPT",
        help="Prompt selector for the processing mode. Optional for -process."
    )

    args = parser.parse_args()

    # Ensure llm_model is required if not listing batches
    if not args.list and args.llm_model is None:
        parser.error("llm_model is required for processing, checking, or exporting.")

    return args

def main() -> None:
    """Main function to parse arguments, validate paths, run LLM model, list, check and export batch process."""
    args: argparse.Namespace = parse_arguments()

    script_dir = Path(__file__).parent
    file_path = script_dir / ".." / ".." / "Private" / "ClientKeys" / f"{args.llm_model}-api.txt"
    if not file_path.exists():
        raise(f"{file_path} does not exist.") 
    common.chatgpt_client = authenticate(str(file_path))

    if args.verbose:
        common.set_verbose(True)
        print("Verbose mode enabled.")
    
    # Case 1: User would like to process image or directory
    # TODO: Implement video processing functionality here
    if args.process:
        if args.prompt:
            common.set_prompt(args.prompt)
        if args.verbose:
            print(f"Processing model: {args.llm_model}, input path: {args.process}")
    
        process_path: Path = Path(args.process)
        process(process_path, args.llm_model)

    # Case 2: User would like to list out all batches processing or processed.
    elif args.list:
        batches_list()

    # Case 3: User would like to check the progress of a given batch_id
    elif args.check:
        check_batch(args.check, args.llm_model)

    # Case 4: User would like to export a completed batch
    elif args.export:
        export_batch(args.export, args.llm_model)

if __name__ == "__main__":
    main()

