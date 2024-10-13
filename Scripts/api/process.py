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
import os 
REQUEST_FUNCTIONS: dict[str, Callable] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request
}

def process_each_model(model_name: str, file_path: Path) -> list[dict[str, Any]]:
    """Helper Function For Process_Each_Model
    Processes for a LLM and returns the result as a dictionary.

    Args:
        model_name: The name of the model to process.
        file_path_str: The path to the file or directory to process.
    """
    if file_path.is_file() and file_path.suffix in common.VALID_EXTENSIONS:
        verbose_print(f"Sending {file_path} to {model_name}...")
        request_output: list[dict[str, Any]] = [REQUEST_FUNCTIONS[model_name](file_path)]

    elif file_path.is_dir():
        verbose_print(f"Sending {file_path} to {model_name}...")
        request_output: list[dict[str, Any]] = parallel_process(file_path, REQUEST_FUNCTIONS[model_name])

    else:
        print(f"{file_path} is not a valid file or directory.")
        sys.exit(1)

        
    return request_output

def process_model(model_name: str, file_path_str: str) -> None:
    """Process a given model and file path and generates a CSV output.
    
    Args:
        model_name: The name of the model to process.
        file_path_str: The path to the file or directory to process.
    """
    verbose_print(f"Processing model: {model_name}")
    verbose_print(f"Prompt Used: {common.prompt}")
    if model_name not in common.LLMS:
        print("Invalid model name")
        sys.exit(1)
    file_path: Path = Path(file_path_str)

    request_output = []
    if model_name == "all":
        for model in ["chatgpt", "gemini", "claude"]:
            request_output = request_output + process_each_model(model, file_path)
    else:
        request_output = process_each_model(model_name, file_path)
    
    generate_csv_output(model_name, request_output)

def generate_csv_output(model_name, data: dict[str, Any], output_directory: Optional[Path] = None):
    """Create a CSV file from the given data.
    
    Args:
        data: The data to convert to a CSV file.
        output_directory: The directory to save the CSV file in. If None, prompts user for location
    """
    

    rows: list[dict[str, Any]] = []


    if model_name == "all":
        images_length: int = int(len(data) / 3)

        for i in range(images_length):
            new_data_row = {}
            new_data_row['ChatGPT File_name'] = data[i]['file_name']
            new_data_row['ChatGPT Model'] = data[i]['model']
            new_data_row['ChatGPT Description'] = data[i]['description']
            new_data_row['ChatGPT Reasoning'] = data[i]['reasoning']
            new_data_row['ChatGPT Action'] = data[i]['action']
            new_data_row['Gemini File_name'] = data[i + images_length]['file_name']
            new_data_row['Gemini Model'] = data[i + images_length]['model']
            new_data_row['Gemini Description'] = data[i + images_length]['description']
            new_data_row['Gemini Reasoning'] = data[i + images_length]['reasoning']
            new_data_row['Gemini Action'] = data[i + images_length]['action']
            new_data_row['Claude File_name'] = data[i + (images_length * 2)]['file_name']
            new_data_row['Claude Model'] = data[i + (images_length * 2)]['model']
            new_data_row['Claude Description'] = data[i + (images_length * 2)]['description']
            new_data_row['Claude Reasoning'] = data[i + (images_length * 2)]['reasoning']
            new_data_row['Claude Action'] = data[i + (images_length * 2)]['action']
            rows.append(new_data_row)
    else:
        for single_data in data:
            row = {
                    'File_name': single_data['file_name'],
                    'Model': single_data['model'],
                    'Description': single_data['description'],
                    'Reasoning': single_data['reasoning'],
                    'Action': single_data['action']
            }

            for key, value in single_data.items():
                if key not in row:
                    row[key.capitalize()] = value
            rows.append(row)
            
    df: pd.DataFrame = pd.DataFrame(rows)
    if output_directory is None:
        csv_file_path = ask_save_location("result.csv")

    if not csv_file_path:
        return False
    try:
        # Save the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)
        
        # Check if the file exists
        if os.path.isfile(csv_file_path):
            verbose_print(f"Results saved to {csv_file_path}")
            return True
        else:
            print("CSV file was not created.")
            return False
    except OSError as e:
        print(f"An error occurred: {e}")   
        raise e 
        return False
        

def parallel_process(dir_path: Path, request_function: Callable) -> list[dict[str, Any]]:
    """Process multiple files in parallel using a request function.

    Args:
        dir_path: A Path object representing the directory containing files to process.
        request_function: A callable that processes each file.

    Returns:
        A list of dictionaries containing results for each file.
    """
    request_output: list = []
    
    # Create a dictionary of valid files to process
    file_dict: dict[str, Path] = get_file_dict(dir_path)
    # chec if dict is empty, if so raise value error
    if not file_dict:
        raise ValueError("No valid files found in the directory.")

    with ThreadPoolExecutor(max_workers=common.MAX_THREAD_WORKERS) as executor:
        future_to_file = {executor.submit(request_function, file): label for label, file in file_dict.items()}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(future_to_file), desc="Processing items"):
            label: str = future_to_file[future]  # Retrieve label for the current file
            try:
                result = future.result()
                if result is not None:
                    verbose_print(f"    {label} processed.")  # Use label to indicate file name
                    request_output.append(result)
            except Exception as e:
                print(f'{label} generated an exception: {e}')  # Corrected to use label for error reporting

    return request_output