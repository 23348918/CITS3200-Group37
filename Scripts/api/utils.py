import pandas as pd
from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
import json
from openai import OpenAI
import sys


def ask_save_location(default_filename: str) -> str:
    """
    Prompt the user to select a location to save a file. If no location is selected, return a default path.

    Args:
        default_filename (str): The default filename to use if the user does not provide one.
        default_directory (str): The default directory to use if the user does not provide a location.

    Returns:
        str: The path selected by the user or the default path if canceled.
    """
    default_directory: str = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    # Initialize Tkinter root
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Prompt the user to select a directory and enter a file name
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=default_filename,
        initialdir=default_directory,
        title="Select location to save your file"
    )
    
    # If no file path is selected, use the default location

    if not file_path:
        print("Cancelled. Exiting.")
        sys.exit(0)
    return file_path

def get_save_path(filename: str, directory: Path):
    """
    Generates a file path in a fixed directory with a specified filename.

    Args:
        default_filename (str): The default filename to use.
        fixed_directory (str): The fixed directory to save the file in.

    Returns:
        Path: The Path object representing the file path.
    """
    # Define the fixed directory and ensure it exists
    dir = Path(directory)
    dir.mkdir(parents=True, exist_ok=True)
    
    # Define the full path with the filename
    file_path = dir / f"{filename}.jsonl"
    
    return file_path

def generate_csv_output(data: Dict[str, Any], output_directory: Optional[Path] = None) -> None:
    """
    Exports the parsed data to a CSV file.

    Args:
        data: The data containing choices and model information.
        output_directory: Directory where the CSV file should be saved. If None, prompts user for location.
    """
    model = data.get('model', '')
    
    if model.startswith('gpt-'):
        # Handle ChatGPT response format
        rows: List[Dict[str, Any]] = [
            {
                'Image_ID': index,
                'Model': model,
                'Description': choice['message']['parsed']['description'],
                'Action': choice['message']['parsed']['action'],
                'Reasoning': choice['message']['parsed']['reasoning']
            }
            for index, choice in enumerate(data.get('choices', []), start=1)
        ]
    
    elif model.startswith('claude-'):
        # Handle Claude response format
        rows: List[Dict[str, Any]] = [
            {
                'Image_ID': 1,  # Assuming single response, set ID to 1
                'Model': model,
                'Description': parse_claude_content(data['content'], 'description'),
                'Action': parse_claude_content(data['content'], 'action'),
                'Reasoning': parse_claude_content(data['content'], 'reasoning')
            }
        ]
    elif model.startswith('models/gemini-'):
        rows: List[Dict[str, Any]] = [
            {
                'Image_ID': 1,  # Assuming single response, set ID to 1
                'Model': model,
                'Description': data['description'],
                'Action': data['action'],
                'Reasoning': data['reasoning']
            }
        ]

    
    else:
        raise ValueError("Unsupported model type")

    df: pd.DataFrame = pd.DataFrame(rows)
    
    if output_directory is None:
        csv_file_path = ask_save_location("result.csv")
    else:
        csv_file_path = output_directory / "result.csv"
    
    df.to_csv(csv_file_path, index=False)
    print(f"Results saved to {csv_file_path}")
    

def parse_claude_content(content: List[Dict[str, str]], field: str) -> str:
    """
    Parses the Claude response content to extract the specified field.

    Args:
        content: The content from the Claude response.
        field: The field to extract (description, action, or reasoning).

    Returns:
        The extracted field value.
    """
    text = content[0]['text'] if content else ''
    field_map = {
        'description': 'Description: ',
        'action': 'Recommended Action: ',
        'reasoning': 'Reason: '
    }
    prefix = field_map.get(field, '')
    
    if prefix:
        parts = text.split('\n\n')
        for part in parts:
            if part.startswith(prefix):
                return part.replace(prefix, '').strip()
    
    return ''



def select_file() -> str:
    """
    Opens a file dialog to select a file.

    Returns:
        The path to the selected file as a string.
    """
    root = tk.Tk()
    root.withdraw()
    file_path: str = filedialog.askopenfilename()

    return file_path

def result_to_dict(content: bytes) -> Dict[str, Any]:

    """
    Converts the binary content of a file to a dictionary.
    
    Args:
        content (bytes): The binary content of the file.
    
    Returns:
        Dict[str, Any]: A dictionary representation of the file content.
    
    Raises:
        UnicodeDecodeError: If there is an error decoding the content.
        json.JSONDecodeError: If there is an error parsing the content.
    """
    try:
        content_str = content.decode('utf-8')
        data_list = [json.loads(line) for line in content_str.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Error decoding or parsing the content: {e}")
        return {}
    
    return(data_list)



def save_batch_results_to_file(dict_response: dict, out_path: str) -> None:
    """
    Saves the batch results to a specified output path.

    Args:
        dict_response: The dictionary containing batch results to be saved.
        out_path: The output path where the file will be saved.

    Raises:
        IOError, OSError: If there is an issue with writing the file.
    """
    try:
        with open(out_path, 'w') as outfile:
            json.dump(dict_response, outfile, indent=4)
        
        if os.path.isfile(out_path):
            print(f"Batch results saved to {out_path}")
        else:
            print(f"File was not created successfully. Batch result was not saved.")
        return True
    except (IOError, OSError) as e:
        print(f"An error occurred while writing the file: {e}")
        return False