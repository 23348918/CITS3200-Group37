import common
from common import verbose_print
from pathlib import Path
from utils import get_file_dict, encode_image, encode_video, create_dynamic_response_model
from process import generate_csv_output
import time
import json
import os
import sys
import openai
from openai import OpenAI
import re




def process_batch(file_path_str: str, auto: bool) -> None:
    """Processes a batch of files located at the given file path, either automatically or manually.

    Args:
        file_path_str: The string representing the path to the file or directory.
        auto: Boolean flag indicating whether to automatically process and export results.
    """
    file_path: Path = Path(file_path_str)
    if file_path.is_dir() or file_path.suffix in common.VALID_EXTENSIONS:
        verbose_print(f"Sending {file_path} to chatgpt...")
        batch_id: str = batch_process_chatgpt(file_path)
        print(f"Batch created with ID: {batch_id}")
        if auto:
            verbose_print("Auto processing and exporting results....")
            time.sleep(common.WAITING_TIMER)
            status, status_message = check_batch(batch_id)
            verbose_print(f"{batch_id} status: {status} \t {status_message}")
            while status in common.PROCESS_STATUS:
                time.sleep(common.WAITING_TIMER)
                status, status_message = check_batch(batch_id)
            if status == "completed":
                export_batch(batch_id)
            else:
                raise RuntimeError(f"Batch processing failed: {status}: {status_message}")

def print_check_batch(batch_id: str) -> None:
    """Prints the status of a batch process by checking its batch ID.
    
    Args:
        batch_id: The ID of the batch to check.
    """
    status, status_message = check_batch(batch_id)
    print(f"{batch_id} status: {status} \t {status_message}")

def check_batch(batch_id: str) -> tuple[str, str]:
    
    
    batch_status_dict = {
    "validating": "the input file is being validated before the batch can begin",
    "failed": "the input file has failed the validation process",
    "in_progress": "the input file was successfully validated and the batch is currently being run",
    "finalizing": "the batch has completed and the results are being prepared",
    "completed": "the batch has been completed and the results are ready",
    "expired": "the batch was not able to be completed within the 24-hour time window",
    "cancelling": "the batch is being cancelled (may take up to 10 minutes)",
    "cancelled": "the batch was cancelled"
}

    """Checks the status of a batch process by its batch ID.
    
    Args:
        batch_id: The ID of the batch to check.
    
    Returns:
        The status and status message of the batch.
    """
    try:
        batch_status = common.chatgpt_client.batches.retrieve(batch_id)
        verbose_print(f"Checking status of batch {batch_id}\t {batch_status.status}")

    except Exception as e:
        raise Exception(f"Check Batch failed: \n{e.body}") from None

    
    if batch_status.error_file_id:
        status_message: str = "Processing failed"
    # elif batch_status.status == "completed":
    #     status_message: str = "Processing success. You can now extract the file the file"
    # else:
    #     status_message: str = "Processing..."   
    else:
        status_message: str = batch_status_dict[batch_status.status]
    return (batch_status.status, status_message)

def export_batch(batch_id: str) -> None:
    """Exports the results of a batch process.
    
    Args:
        batch_id: The ID of the batch to export.
    """
    verbose_print(f"Exporting batch {batch_id}...")
    try:
        batch_results: OpenAI = common.chatgpt_client.batches.retrieve(batch_id)
    except openai.AuthenticationError as e: #authention error
        raise ValueError(f"Export Batch Failed: {e.response} {e.code}\n{e.body}") from e
    except openai.BadRequestError as e: # bad request error - no batchID exists
        raise NameError(f"Export Batch Failed: {e.param} {e.code}\n{e.body}") from None
    except Exception as e: # for all other error issues
        raise Exception(f"Error exporting batche: {e}") from None
    
    if batch_results.error_file_id: # exporting a batch result that failed
        print(f"Batch ID:{batch_id} Batch status: {batch_results.status} - failed. Cannot export results. \nTerminating....")
        delete_exported_files(common.chatgpt_client, batch_results)
        sys.exit(1)
        

    
    output_file_id: str = batch_results.output_file_id
    try:
        common.chatgpt_client.files.retrieve(output_file_id)
    except Exception as e:
        raise Exception(e) from None


    response_bytes: bytes = common.chatgpt_client.files.content(output_file_id).read()
    response_dicts: list[dict[str, str]] = bytes_to_dicts(response_bytes)
    
    extportResult = generate_csv_output(response_dicts)
    
    
    
    if extportResult:
        delete_exported_files(common.chatgpt_client, batch_results)
        verbose_print(f"Cleaning up batch relevant files.")
    else:
        print(f"Cancelled. BatchID: {batch_id}" )
        print(f"To export results using the export command, see python3 main.py -h for more info.")    
    

def bytes_to_dicts(response_bytes: bytes) -> list[dict[str, str]]:
    """Converts a byte response to a list of dictionaries.
    
    Args:
        response_bytes: The byte response to convert.
        
    Returns:
        A list of dictionaries containing the response data.
    """
    response_str: str = response_bytes.decode("utf-8")
    response_lines: list[str] = response_str.splitlines()
    response_dicts: list = []
    DynamicAnalysisResponse = create_dynamic_response_model(common.custom_str)
    print("DynamicAnalysisResponse.model_fields:", DynamicAnalysisResponse.model_fields)
    for line in response_lines:
        json_obj: dict = json.loads(line)
        file_name: str = json_obj['id']
        model: str = json_obj['response']['body']['model']
        content: str = json_obj['response']['body']['choices'][0]['message']['content'].replace("*", "")
        pattern: re.Pattern = re.compile(r'(\w+):\s*(.*?)(?=\n\w+:|$)', re.DOTALL | re.IGNORECASE)
        matches: list[tuple[str, str]] = pattern.findall(content)
        response_dict: dict[str, str] = {match[0].lower(): match[1].strip() for match in matches}
        response_dict['file_name'] = file_name
        response_dict['model'] = model
        response_dicts.append(response_dict)
    return response_dicts
    

def list_batches() -> None:
    """Lists the past 20 batches and their status'."""
    try:
        verbose_print("Listing all batches.")
        batch_list: list = common.chatgpt_client.batches.list(limit=20)
        for item in batch_list:
            result: str = "Batch process success." if not item.error_file_id else "Batch process failed"
            print(f"Batch ID: {item.id}\tStatus: {item.status}\t result:{result}")
    except openai.AuthenticationError as e:
        # Raise the original AuthenticationError as a ValueError
        raise ValueError(f"List Batch Failed: {e.response} {e.code}\n{e.body}") from e
    except Exception as e: # for all other error issues
        raise Exception(f"Error listing batches: {e}") from None

def batch_process_chatgpt(dir_path: Path) -> str:
    """Processes a batch of files located at the given directory path.
    
    Args:
        dir_path: The path to the directory containing the files.
        
    Returns:
        The ID of the batch created."""
    file_dict: dict[str, Path] = get_file_dict(dir_path)
    file_name: str = dir_path.stem
    out_path: Path = Path("../../Batch_Files") / f"{file_name}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    generate_batch_file(file_dict, out_path)
    verbose_print(f"Batch file saved to {out_path}")
    return upload_batch_file(out_path)

def generate_batch_file(file_dict: dict[str, Path], out_path: Path) -> None:
    """Generates a batch file from a dictionary of files.
    
    Args: 
        file_dict: The dictionary of files to include in the batch.
        out_path: The path to save the batch file."""
    if not file_dict:
        raise ValueError("No files found in the directory.")
    try:
        with open(out_path, "w") as f:
            for label, file_path in file_dict.items():
                # This assumes filtering by file extensions is already done, but add here for extra safety
                if file_path.suffix not in common.VALID_EXTENSIONS:
                    verbose_print(f"Skipping {file_path}. Unsupported file format.")
                    continue
                json_entry = create_json_entry(label, file_path)
                json.dump(json_entry, f)
                f.write("\n")  # Ensure each JSON entry is on a new line

    except OSError as e:
        raise OSError(f"Failed to write the batch file: {e}")
    
    if not os.path.exists(out_path):
        raise FileNotFoundError(f"Batch file not found at {out_path}")

def create_json_entry(label: str, file_path: Path) -> dict[str, str]:
    """Creates an entry for a batch file.

    Args:
        file_path: The path of the image file.

    Returns:
        A dictionary representing the entry for the batch file.
    """
    encoded_media = None
    if file_path.suffix in common.VIDEO_EXTENSIONS:
        encoded_media = encode_video(file_path)
    else:
        encoded_media  = encode_image(file_path)
    
    json_entry: dict = {
        "custom_id": label,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": common.prompt,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the following image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_media}"
                            },
                        },
                    ],
                },
            ],
        },
    }
    return json_entry

def upload_batch_file(batch_file_path: Path) -> str:
    """Uploads a batch file to the ChatGPT API.

    Args:
        batch_file_path: The path to the batch file.

    Returns:
        The ID of the uploaded batch.
    """
    if not batch_file_path.is_file():
        raise FileNotFoundError(f"Batch file not found: {batch_file_path}")
    
    if not batch_file_path.suffix.lower() == '.jsonl':
        raise ValueError(f"Invalid file type: {batch_file_path}. Only '.jsonl' files are accepted.")
    
    if os.path.getsize(batch_file_path) > 99 * 1024 * 1024:
        print("Processing limit of 99MB reached. Please reduce number of files to be processed.\nTerminating....")
        raise ValueError("File size exceeds the limit of 99MB.")
    elif os.path.getsize(batch_file_path) == 0:
        raise ValueError("File is empty.")
    


    try:
        with open(batch_file_path, "rb") as file:
            batch_input_file: OpenAI = common.chatgpt_client.files.create(
                file=file,
                purpose="batch"
            )
    
    except FileNotFoundError:
        print(f"Error: File not found: {batch_file_path}.")
        raise 
    except PermissionError:
        print(f"Error: Permission denied for file {batch_file_path}.")
        raise
    except openai.APIError as e:
        print(f"Error uploading batch file: {e}")
        raise
    

    batch_id: str = common.chatgpt_client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    ).id
    return batch_id


def delete_exported_files(client: OpenAI, batch_results) -> None:
    """
    Deletes the exported files after saving the batch results.

    Args:
        client: Authenticated OpenAI client.
        batch_results: The batch results object.

    Returns:
        None
    """


    if batch_results.input_file_id:
        # client.files.delete(batch_results.input_file_id)
        try:
            common.chatgpt_client.files.delete(batch_results.input_file_id)
            verbose_print(f"Cleaning input file")
        except Exception as e:
            pass

    if batch_results.output_file_id:
        # client.files.delete(batch_results.output_file_id)
        try:
            common.chatgpt_client.files.delete(batch_results.output_file_id)
            verbose_print(f"Cleaing output file")

        except Exception as e:
            pass

    if batch_results.error_file_id:
        # client.files.delete(batch_results.error_file_id)
        try:
            common.chatgpt_client.files.delete(batch_results.error_file_id)
            verbose_print(f"Cleaing error file")

        except Exception as e:
            pass
            
            
    
    