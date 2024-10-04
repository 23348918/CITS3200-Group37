import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
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

        # Check the structure of the result and store the entire response
        if isinstance(result, dict):
            result_dict.update(result)  # Add the entire response to result_dict
        else:
            result_dict.update({"description": "Error processing file", "reasoning": "", "action": ""})

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        result_dict.update({"description": "Error processing file", "reasoning": "", "action": ""})

    return result_dict 


def parallel_process(file_dict: Dict[str, Path], num_workers=10,):
    """
    Process multiple files in parallel with Claude using a dictionary input.

    Args:
        file_dict: Dictionary where keys are labels and values are file paths.
        output_file: Path to save the results as a JSON
        num_workers: Number of parallel workers to use.

    Returns:
        A list of dictionaries containing results for each file.
    """
    processed_results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_file = {executor.submit(process_item, label, file_path): label for label, file_path in file_dict.items()}
        for future in tqdm(concurrent.futures.as_completed(future_to_file), total=len(future_to_file), desc="Processing items"):
            label = future_to_file[future]
            try:
                result = future.result()
                if result is not None:
                    processed_results.append(result)
            except Exception as e:
                print(f'Label {label} generated an exception: {e}')
                
    return processed_results
    

