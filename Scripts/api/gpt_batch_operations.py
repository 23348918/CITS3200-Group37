from openai import OpenAI
from utils import result_to_dict, save_batch_results_to_file, check_file_size
import openai
import common

def upload_batch_file(client: OpenAI, file_path: str) -> OpenAI:
    """
    Uploads a JSONL file to be processed as a batch.

    Args:
        file_path: Path to the batch input file.

    Returns:
        The uploaded batch file object.

    Raises:
        Exception: If the upload fails or the file cannot be accessed.
    """
    if not check_file_size(file_path):
        print(f"Processing limit of 99MB reached. Please reduce number of files to be processed.\nTerminating....")
        exit(1)


    try:
        with open(file_path, "rb") as file:
            batch_input_file: OpenAI = client.files.create(
                file=file,
                purpose="batch"
            )
        return batch_input_file
    
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}. Please check the file path.")
        raise
    except PermissionError:
        print(f"Error: Permission denied for file {file_path}.")
        raise
    except openai.APIError as e:
        print(f"Error uploading batch file: {e}")
        raise


def create_batch_file(client: OpenAI, upload_batch: OpenAI) -> OpenAI:
    """
    Creates a batch object for processing the uploaded file.

    Args:
        client: Authenticated OpenAI client.
        upload_batch: Uploaded batch file object.

    Returns:
        OpenAI: The created batch object.
    """
    batch = client.batches.create(
        input_file_id=upload_batch.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    # client.files.delete(upload_batch.id)  # Clean up and delete the uploaded file. Unnecessary after batch completion.
    return batch

def list_batches(client: OpenAI) -> None:
    """
    Lists all batch processes.

    Args:
        client: Authenticated OpenAI client.
    
    Prints batch information to the console.
    """
    batch_list = client.batches.list(limit=100)
    for item in batch_list:
        result = "Batch process success." if not item.error_file_id else "Batch process failed"
        print(f"Batch ID: {item.id}\tStatus: {item.status}\t result:{result}")

def check_batch_process(client: OpenAI, batch_id: str) -> str:
    """
    Checks the status of a specified batch.

    Args:
        client: Authenticated OpenAI client.
        batch_id: The ID of the batch to check.

    Returns:
        str: Status of the batch.
    """
    try:
         
        batch_status = client.batches.retrieve(batch_id)
    except Exception as e:
        print(f"Batch ID {batch_id} not found")
        exit(1) # exit the program if batch ID not found
    if batch_status.error_file_id:
        status_message = "Processing failed"
    else:
        status_message = "Processing success. You can now extract the file the file"

    # result = f"{batch_id} status: {batch_status.status} \t {status_message}"

    return (batch_status.status, status_message)

def delete_exported_files(client: OpenAI, batch_results) -> None:
    """
    Deletes the exported files after saving the batch results.

    Args:
        client: Authenticated OpenAI client.
        batch_results: The batch results object.

    Returns:
        None
    """

    if common.verbose:
        print("Cleaning up generated files.")

    if batch_results.input_file_id:
        client.files.delete(batch_results.input_file_id)
        # print (batch_results.input_file_id)

    if batch_results.output_file_id:
        client.files.delete(batch_results.output_file_id)
        # print (batch_results.output_file_id)

    if batch_results.error_file_id:
        client.files.delete(batch_results.error_file_id)
        # print (batch_results.error_file_id)

def export_batch_result(client: OpenAI, batch_id: str, out_path: str) -> None:
    """
    Fetches batch results and saves them to a specified file.

    Args:
        client (OpenAI): OpenAI client instance.
        batch_id (str): The ID of the batch to retrieve.
        out_path (str): The output path where the results will be saved.
    Returns:
        None
    """
    try:
        batch_results: OpenAI = client.batches.retrieve(batch_id)
    except Exception as e:
        print(f"Batch ID {batch_id} not found: {e}")
        return False
    

        
    if batch_results.error_file_id:
        print(f"Batch processing was unsuccessful for {batch_id}.")
        output_file_id: str = batch_results.error_file_id
    else:
        output_file_id: str = batch_results.output_file_id
    
 
        
    try:
        test = client.files.retrieve(output_file_id)
    except Exception:
        print(f"You can only export the file once. Please rerun the process to re-export the results again.")
        exit(1)
    
    result: bytes = client.files.content(output_file_id).read()
    dict_response: dict = result_to_dict(result)
     # Return False if failed to retrieve batch results
    
    #TODO: Instead of saving to json, extract data and save to csv. 
    # Modift and chekc function save_batch_results_to_file in utils.py
    if save_batch_results_to_file(dict_response, out_path): # if true, then successfully saved
        delete_exported_files(client, batch_results)
    # return True




