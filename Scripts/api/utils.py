import pandas as pd
from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
import json
from openai import OpenAI
import sys


def ask_save_location(default_filename):
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

def generate_csv_output(data: Dict[str, Any], output_directory: Optional[Path] = None) -> None:
    """
    Exports the parsed data to a CSV file.

    Args:
        data: The data containing choices and model information.
        csv_file_path: Path to the output CSV file. Defaults to 'output.csv'.
    """
    rows: List[Dict[str, Any]] = [
        {
            'Image_ID': index,
            'Model': data['model'],
            'Description': choice['message']['parsed']['description'],
            'Action': choice['message']['parsed']['action'],
            'Reasoning': choice['message']['parsed']['reasoning']
        }
        for index, choice in enumerate(data['choices'], start=1)
    ]
    
    df: pd.DataFrame = pd.DataFrame(rows)
    csv_file_path = ask_save_location("result.csv")
    df.to_csv(csv_file_path, index=False)


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

# for converting the binary content of a file to a dictionary. used in 
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
    
    # Print the data
    # print(json.dumps(data_list, indent=4))
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