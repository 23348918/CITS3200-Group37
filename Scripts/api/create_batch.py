import json
import os
import base64
import sys
import common
import tkinter as tk
from tkinter import filedialog
from typing import Optional, List
from pathlib import Path
from gpt_request import encode_image, encode_video


def get_directory(action_name: str) -> Optional[str]:
    """
    Prompt the user to select a directory that contains images to process.
    Calls getfilepaths to check if the selected directory contains any supported image files.
    If no supported image files are found, the script exits.

    Args:
        action_name (str): Title of the dialog window.

    Returns:
        Optional[str]: List of paths to image files or None if no supported image files are found.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    selected_directory  = filedialog.askdirectory(title=action_name, initialdir=os.path.abspath(__file__))
    if not selected_directory :
        return None
    
    image_file_paths = get_file_paths(selected_directory)
    if not image_file_paths:
        print("No supported image files found in the selected directory. Please select a directory containing images.")
        sys.exit(0)
    return image_file_paths

def get_file_paths(directory_path: str) -> list[str]:
    """
    Recursively get all image file paths from a directory or return a single file path if it's an image.
    
    Args:
        directory_path (str): Path to a file or directory.

    Returns:
        List[str]: List of image file paths.
    """
    image_file_paths = []

    # If the path is a file, check its extension and return it if it's an image
    if os.path.isfile(directory_path):
        _, extension = os.path.splitext(directory_path)
        if extension.lower() in common.VALID_EXTENSIONS:
            return [directory_path]
        else:
            print(f"Skipping unsupported file: {os.path.basename(directory_path)}")
            return []

    # If the path is a directory, recursively get image file paths
    elif os.path.isdir(directory_path):
        for entry in os.listdir(directory_path):
            full_path = os.path.join(directory_path, entry)
            image_file_paths.extend(get_file_paths(full_path))  # Recursive call
    
    return image_file_paths

# def encode_image(image_path):
#     """
#     Encodes the image located at the given image_path into base64 format.

#     Parameters:
#     image_path (str): The path to the image file.

#     Returns:
#     str: The base64 encoded representation of the image.
#     """
#     with open(image_path, "rb") as image_file:
#         res = base64.b64encode(image_file.read()).decode('utf-8')
#     return res

def create_entry(item):
    """
    Creates an entry for a batch file.

    Args:
        filepath (str): The path of the image file.

    Returns:
        dict: A dictionary representing the entry for the batch file.

    """
    
    filepath = Path(item)
    encoded_media = None
    if filepath.suffix in common.VIDEO_EXTENSIONS:
        encoded_media = encode_video(filepath)
    else:
        encoded_media  = encode_image(filepath)

    currentDict = {
        "custom_id": item,
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
    return currentDict

def ask_save_location(outputName: str = "batchfile.jsonl") -> str:
    """
    Prompt the user to select a location to save a file. If no location is selected, return a default path.

    Args:
        outputName (str): The default filename to use if the user does not provide one.

    Returns:
        str: The path selected by the user or the default path if canceled.
    """
    root = tk.Tk()
    root.withdraw()
    default_directory: str = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    # Prompt the user to select a directory and enter a file name
    file_path: str = filedialog.asksaveasfilename(
        defaultextension=".jsonl",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=outputName,
        initialdir=default_directory,
        title="Select location to save your file"
    )
    
    if not file_path:
        print("Cancelled. Exiting.")
        sys.exit(0)
    return file_path

def generate_batch_file(filePaths: List[str], outfile: str) -> None:
    """
    Generate a batch file containing image file paths.
    
    Args:
        filePaths (List[str]): List of image file paths.
        outfile (str): Output path for the batch file.
    """
    with open(outfile, "w") as file: 
        for item in filePaths:
            entry = create_entry(item)
            json.dump(entry, file)
            file.write("\n")

    if not os.path.isfile(outfile):
        print("File was not created.")
        sys.exit(1)


    
    
    

