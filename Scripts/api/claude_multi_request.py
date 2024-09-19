# still needs working on

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from pathlib import Path
import common
from claude_request import analyse_image, analyse_video
from tqdm import tqdm

def process_item(label: str, file_path: Path) -> Dict[str, Any]:
    """
    Process a single image or video file with Claude and include the label.

    Args:
        label: A descriptive label for the file.
        file_path: Location of the media file to be processed.

    Returns:
        A dictionary containing the label and results for each file.
    """
    result_dict = {"label": label}
    try:
        # Initialize the API client here if needed
        if file_path.suffix in common.VIDEO_EXTENSIONS:
            result = analyse_video(file_path)
        else:
            result = analyse_image(file_path)
        
        # Ensure result is a dictionary with the correct fields
        if isinstance(result, dict):
            result_dict["description"] = result.get("description", "Description not available")
            result_dict["reasoning"] = result.get("reasoning", "Reasoning not available")
            result_dict["action"] = result.get("action", "Action not available")
        else:
            result_dict.update({"description": "Error processing file", "reasoning": "", "action": ""})
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        result_dict.update({"description": "Error processing file", "reasoning": "", "action": ""})
    
    return result_dict

def parallel_process(file_dict: Dict[str, Path], num_workers=10) -> List[Dict[str, Any]]:
    """
    Process multiple files in parallel with Claude using a dictionary input.

    Args:
        file_dict: Dictionary where keys are labels and values are file paths.
        num_workers: Number of parallel workers to use.

    Returns:
        A list of dictionaries containing results for each file.
    """
    results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_file = {executor.submit(process_item, label, file_path): label for label, file_path in file_dict.items()}
        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(future_to_file), desc="Processing items"):
            label = future_to_file[future]
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                print(f'Label {label} generated an exception: {e}')
    
    return results

def get_file_dict(directory_path: Path) -> Dict[str, Path]:
    """
    Generate a dictionary of file paths and labels from a directory.

    Args:
        directory_path: The path to the directory containing files.

    Returns:
        A dictionary where keys are file names and values are full file paths.
    """
    file_dict = {}
    for file_path in directory_path.glob('*'):
        if file_path.is_file():
            file_dict[file_path.name] = file_path
    return file_dict



