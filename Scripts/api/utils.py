import pandas as pd
from typing import List, Dict, Any, Optional
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os


def ask_save_location(default_filename="result.csv", default_directory="../../Output"):
    """
    Prompt the user to select a location to save a file. If no location is selected, return a default path.

    Args:
        default_filename (str): The default filename to use if the user does not provide one.
        default_directory (str): The default directory to use if the user does not provide a location.

    Returns:
        str: The path selected by the user or the default path if canceled.
    """
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
    if not os.path.exists(default_directory):
        os.makedirs(default_directory)

    if not file_path:

        file_path = os.path.join(default_directory, default_filename)
    
    return file_path

def generate_csv_output(data: Dict[str, Any], output_directory: Optional[Path] = None) -> None:
    """Exports the parsed data to a CSV file.

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
    csv_file_path = ask_save_location()
    df.to_csv(csv_file_path, index=False)





def select_file() -> str:
    """Opens a file dialog to select a file.

    Returns:
        The path to the selected file as a string.
    """
    root = tk.Tk()
    root.withdraw()
    file_path: str = filedialog.askopenfilename()

    return file_path