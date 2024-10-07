import common
from common import verbose_print
import sys
from pathlib import Path
from llm_requests import chatgpt_request, gemini_request, claude_request
from utils import get_file_dict, ask_save_location
from typing import Callable, Any, Optional
from tqdm import tqdm
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import time


REQUEST_FUNCTIONS: dict[str, Callable] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request
}

def process_model(model_name: str, file_path_str: str, auto: bool):
    verbose_print(f"Processing model: {model_name}")
    if model_name not in common.LLMS:
        print("Invalid model name")
        sys.exit(1)
    file_path: Path = Path(file_path_str)

    if file_path.is_file() and file_path.suffix in common.VALID_EXTENSIONS:
        verbose_print(f"Sending {file_path} to {model_name}...")
        request_output: list[dict[str, Any]] = [REQUEST_FUNCTIONS[model_name](file_path)]

    elif file_path.is_dir():
        verbose_print(f"Sending {file_path} to {model_name}...")
        request_output: list[dict[str, Any]] = parallel_process(file_path, REQUEST_FUNCTIONS[model_name])
    
    else:
        print(f"{file_path} is not a valid file or directory.")
        sys.exit(1)

    generate_csv_output(request_output)

def process_batch(model_name: str, file_path_str: str, auto: bool):
    file_path: Path = Path(file_path_str)
    if file_path.is_dir() and model_name == "chatgpt":
        verbose_print(f"Sending {file_path} to {model_name}...")
        batch_id = batch_process_chatgpt(file_path)
        print(f"Batch created with ID: {batch_id}")
        if auto:
            verbose_print("Auto processing and exporting results....")
            time.sleep(common.WAITING_TIMER)
            status, status_message = check_batch(batch_id)
            verbose_print(f"{batch_id} status: {status} \t {status_message}")
            while status not in common.PROCESS_STATUS:
                time.sleep(common.WAITING_TIMER)
                status, status_message = check_batch(batch_id)
            export_batch(batch_id)
    pass

def check_batch(): 
    pass

def export_batch():
    pass

def list_models():
    pass

def generate_csv_output(data: dict[str, Any], output_directory: Optional[Path] = None) -> None:
    """
    Exports the parsed data to a CSV file, handling both single and multi-image Claude responses.

    Args:
        data: The data containing Claude API response, either a single response or multiple.
        model: The model name (e.g., 'claude').
        output_directory: Directory where the CSV file should be saved. If None, prompts user for location.
    """
    rows: list[dict[str, Any]] = [
        {
            'File_Name': single_data['file_name'],
            'Model': single_data['model'],
            'Description': single_data['description'],
            'Reasoning': single_data['reasoning'],
            'Action': single_data['action']
        }
        for single_data in data
    ]
    df: pd.DataFrame = pd.DataFrame(rows)
    if output_directory is None:
        csv_file_path = ask_save_location("result.csv")
    else:
        csv_file_path = output_directory / "result.csv"
    df.to_csv(csv_file_path, index=False)
    verbose_print(f"Results saved to {csv_file_path}")

def parallel_process(dir_path: Path, request_function: Callable) -> list[dict[str, Any]]:
    """
    Process multiple files in parallel using a request function.

    Args:
        dir_path: A Path object representing the directory containing files to process.
        request_function: A callable that processes each file.

    Returns:
        A list of dictionaries containing results for each file.
    """
    request_output = []
    
    # Create a dictionary of valid files to process
    file_dict: dict[str, Path] = get_file_dict(dir_path)

    with ThreadPoolExecutor(max_workers=common.MAX_THREAD_WORKERS) as executor:
        future_to_file = {executor.submit(request_function, file): label for label, file in file_dict.items()}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(future_to_file), desc="Processing items"):
            label = future_to_file[future]  # Retrieve label for the current file
            try:
                result = future.result()
                if result is not None:
                    verbose_print(f"    {label} processed.")  # Use label to indicate file name
                    request_output.append(result)
            except Exception as e:
                print(f'{label} generated an exception: {e}')  # Corrected to use label for error reporting

    return request_output

def batch_process_chatgpt(dir_path: Path) -> str:
    # file_paths: list[Path] = get_file_paths(dir_path)
    # file_name: str = dir_path.stem
    # batch_file_location: Path = Path("../../Batch_Files") / f"{file_name}.json"
    # generate_batch_file(file_paths, batch_file_location)
    # verbose_print(f"Batch file saved to {batch_file_location}")
    # return upload_batch_file(batch_file_location)
    pass

def get_file_paths(dir_path: Path) -> list[Path]:
    """Get a list of file paths from a directory.

    Args:
        dir_path: Path to the directory containing files.

    Returns:
        A list of Path objects for each file in the directory.
    """
    # return [file for file in dir_path.iterdir() if file.is_file() and file.suffix in common.VALID_EXTENSIONS]


