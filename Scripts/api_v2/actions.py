import common
from common import verbose_print
import sys
from pathlib import Path
from llm_requests import chatgpt_request, gemini_request, claude_request
from utils import generate_csv_output, get_file_dict
from typing import Callable, Any, List, Dict
from tqdm import tqdm
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

REQUEST_FUNCTIONS: dict[str, Callable] = {
    "chatgpt": chatgpt_request,
    "gemini": gemini_request,
    "claude": claude_request
}

EXTENDED_MODEL_NAMES: dict[str, str] = {
    "gemini": "models/gemini-1.5-pro",
    "chatgpt": "chatgpt-4o-mini",
    "claude": "claude-3-opus-20240229"
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
    
    generate_csv_output(request_output, EXTENDED_MODEL_NAMES[model_name])

def check_model(): 
    pass

def export_model():
    pass

def list_models():
    pass



def parallel_process(dir_path: Path, request_function: Callable) -> List[Dict[str, Any]]:
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
    file_dict: Dict[str, Path] = get_file_dict(dir_path)

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




