# Description: This script processes a batch file using the OpenAI API.
# This uses the output of createBatchFile.py to process a batch file.

# Usage: python3 batch_processing.py <llm_model> <option> <batch_file>
# Example: python3 batch_processing.py chatgpt -process_batch full_path_to_batch_file.jsonl
# Example: python3 batch_processing.py chatgpt -list_batches
# Example: python3 batch_processing.py chatgpt -check_batch <batch_id>
# Example: python3 batch_processing.py chatgpt -export_batch <batch_id>
# NOTE: The batch file must be in JSONL format. (already set in createBatchFile.py)
# NOTE: The file path must be full path.

from openai import OpenAI
import argparse
from auth import authenticate
from utils import ask_save_location, result_to_dict
import json

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for batch processing an LLM model.
    
    Returns:
        Parsed command-line arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run and select option to process a batch file, check the status of the batch, list all batches, or download the batch results."
    )
    
    # Required positional argument for selecting the LLM model
    parser.add_argument(
        "llm_model",
        type=str,
        choices=["chatgpt", "gemini", "claude", "llama"],
        help="Name of the LLM model to process image or video files"
    )
    
    # Mutually exclusive group: only one of these can be provided
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-process_batch",
        type=str,
        metavar="BATCH_FILEPATH",
        help="Tells the program to process the batch file."
    )
    group.add_argument(
        "-list_batches",
        action="store_true",
        help="Tells the program to list all batches."
    )
    group.add_argument(
        "-check_batch",
        type=str,
        metavar="BATCH_ID",
        help="Tells the program to check the status of a batch."
    )

    group.add_argument(
        "-export_batch",
        type=str,
        metavar="BATCH_ID",
        help="Tells the program to export the results of a batch."
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enables verbose output."
    )
    
    return parser.parse_args()


def upload_batch_file(client: OpenAI, file_path: str) -> OpenAI:
    """Uploads a JSONL file to be processed as a batch.

    Args:
        file_path: Path to the batch input file.

    Returns:
        The uploaded batch file object.
    """
    batch_input_file: OpenAI = client.files.create(
        file=open(file_path, "rb"),
        purpose="batch"
    )
    return batch_input_file


def create_batch_file(client: OpenAI, upload_batch: OpenAI, description: str = "Default Description") -> OpenAI:
    """Creates a batch object for LLM to process, requires the output of upload_batch_file function.

    Args:
        upload_batch (OpenAI.File): The uploaded batch file object.
        description (str, optional): Description of the batch. Defaults to "Default Description".

    Returns:
        OpenAI.Batch: The created batch object.
    """
    batch_object: OpenAI.Batch = client.batches.create(
        input_file_id=upload_batch.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": description}
    )
    
    client.files.delete(upload_batch.id)    #after creating the batch, delete the uploaded file
    return batch_object


def list_batches(client: OpenAI) -> OpenAI:
    """Returns a list of all batch processes.

    Args:
        limit: The maximum number of batch processes to return. Defaults to 20.

    Returns:
        OpenAI.BatchList: A list of all batch processes.
    """
    batch_list: OpenAI = client.batches.list(limit=100)
        # for item in batch_list:
    if batch_list:
        for item in batch_list:
            print(f"Batch ID: {item.id} \t")
            if item.error_file_id:
                print(f"Batch Status: {item.status}\tBatch process failed")
            else:
                print(f"Batch Status: {item.status}\tBatch process completed successfully.")
            print()
    else:
        print("No batch process found.")


def check_batch_process(client: OpenAI, batch_id: str) -> OpenAI:
    """Returns the status of the batch requested.

    Args:
        batch_id: The ID of the batch to check.

    Returns:
        The status of the requested batch.
    """
    batch_status: OpenAI = client.batches.retrieve(batch_id)
    return batch_status.status


#TODO: Instead of saving to json, extract data and save to csv
def export_batch_result (client: OpenAI, batch_id: str) -> None:
    """Saves the results of a batch to a JSON file.

    Args:
        batch_id: The ID of the batch to save.
        outpath: The output path for the JSON file.
    """
    
    batch_results = client.batches.retrieve(batch_id)

    file_ID = client.files.content(batch_results.output_file_id)
    
    result = file_ID.read()  # Use read() to get the content as bytes
    
    dict_response = result_to_dict(result) # filter out the resp
    
    # NOTE: Need to change this to save to CSV instead of JSON Before calling this, convert dict to csv
    location = ask_save_location("batchResult.json") # Change the suffix to .csv

    with open(location, 'w') as outfile:
        json.dump(dict_response, outfile, indent=4)
    
    print(f"Batch results saved to {location}")
    
# ------------------- main--------------main--------------------main-------main-------
args: argparse.Namespace = parse_arguments()

print (args)
client: OpenAI = authenticate("../../Private/ClientKeys/chatgpt-api.txt")


if args.process_batch:
    upload_batch: OpenAI = upload_batch_file(client, args.process_batch)
    batch_object: OpenAI = create_batch_file(client, upload_batch)
    print(f"Batch created with ID: {batch_object.id}")
if args.list_batches:
    batch_list: OpenAI = list_batches(client)
if args.check_batch:
    batch_status: OpenAI = check_batch_process(client, args.check_batch)
    print(f"Batch ID {args.check_batch} status: \t {batch_status}")
if args.export_batch:
    batch_results: OpenAI = export_batch_result(client, args.export_batch)


