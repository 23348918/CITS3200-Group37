import pandas as pd
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

def to_csv(data: Dict[str, Any], csv_file_path: Optional[str] = 'output.csv') -> None:
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