import argparse
from auth import authenticate
from batch_operations import upload_batch_file, create_batch_file, list_batches, check_batch_process, export_batch_result
from utils import ask_save_location
from openai import OpenAI

def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for batch processing tasks.

    Sets up command-line options to process a batch file, list batches, check batch status, 
    or export batch results.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """    
    
    parser = argparse.ArgumentParser(description="Batch proc:essing with OpenAI API.")
    parser.add_argument("llm_model", choices=["chatgpt", "gemini", "claude", "llama"], help="LLM model")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-process_batch", metavar="BATCH_FILEPATH", help="Process the batch file.")
    group.add_argument("-list_batches", action="store_true", help="List all batches.")
    group.add_argument("-check_batch", metavar="BATCH_ID", help="Check the status of a batch.")
    group.add_argument("-export_batch", metavar="BATCH_ID", help="Export the results of a batch.")
    
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    
    return parser.parse_args()


def main():
    """Main function to process batch files."""
    args: argparse.Namespace = parse_arguments()
    # client: OpenAI = authenticate("../../Private/ClientKeys/chatgpt-api.txt")
    client: OpenAI = authenticate("../../Private/LanceKeys/APIKey.txt")

    if args.process_batch:
        upload_batch = upload_batch_file(client, args.process_batch)
        batch_object = create_batch_file(client, upload_batch)
        print(f"Batch created with ID: {batch_object.id}")
    
    if args.list_batches:
        list_batches(client)
    
    if args.check_batch:
        status = check_batch_process(client, args.check_batch)
        print(status)
    
    if args.export_batch:
        location = ask_save_location("batchResult.json")
        print(location)
        export_batch_result(client, args.export_batch, location)

if __name__ == "__main__":
    main()
