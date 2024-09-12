# Description: This script generates a batch file for the OpenAI API. 
# The batch file contains image file paths that are to be analyzed by the API.

# Usage: python3 createBatchFile.py [<dirpath> | <imgpath>]
# Provide the path to a directory containing images or a single image file as an argument to the script.
# If no argument is provided, the user is prompted to select a directory containing images.
# The user is prompted again to select a location to save the batch file.


import json
import os
import base64
import sys
import tkinter as tk
from tkinter import filedialog
from typing import Optional
from typing import List

PROMPT : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. "
    "The user will provide you with an image or images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
    "1. Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
    "2. Recommended Action: In few words, give suggestion as to what action should be taken by the driver. "
    "Also include if driver can change lane, overtake or turn left/right.\n"
    "3. Reason: Explain in few words the reason for recommended action.\n\n"
)


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
    image_extensions = {".png", ".jpeg", ".jpg", ".gif", ".webp"}
    image_file_paths = []

    # If the path is a file, check its extension and return it if it's an image
    if os.path.isfile(directory_path):
        _, extension = os.path.splitext(directory_path)
        if extension.lower() in image_extensions:
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

def encode_image(image_path):
    """
    Encodes the image located at the given image_path into base64 format.

    Parameters:
    image_path (str): The path to the image file.

    Returns:
    str: The base64 encoded representation of the image.
    """
    with open(image_path, "rb") as image_file:
        res = base64.b64encode(image_file.read()).decode('utf-8')
    return res

def createEntry(filepath):
    """
    Creates an entry for a batch file.

    Args:
        filepath (str): The path of the image file.

    Returns:
        dict: A dictionary representing the entry for the batch file.

    """
    encodedImage  = encode_image(filepath)
    currentDict = {
        "custom_id": filepath,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the following image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encodedImage}"
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

def generateBatchFile(filePaths: List[str], outfile: str) -> None:
    """
    Generate a batch file containing image file paths.
    
    Args:
        filePaths (List[str]): List of image file paths.
        outfile (str): Output path for the batch file.
    """
    with open(outfile, "w") as file: 
        for item in filePaths:
            entry = createEntry(item)
            json.dump(entry, file)
            file.write("\n")

    if os.path.isfile(outfile):
        print(f"Batch file saved to {outfile}.")
        sys.exit(0)
    else:
        print("File was not created.")
        sys.exit(1)


# ~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~
if len(sys.argv) >1:
    if not os.path.exists(sys.argv[1]):
        print(f"'{sys.argv[1]}' is not a valid path. Ensure full path is entered")
        sys.exit(1)
    dirpath = get_file_paths(sys.argv[1])
elif len(sys.argv) == 1:
    dirpath = get_directory("Select a directory containing images")
    if not dirpath:
        print("Usage: python3 createBatchFile.py [<dirpath> | <imgpath>]")
        sys.exit(1)
else:
    print("Usage: python3 createBatchFile.py [<dirpath> | <imgpath>]")
    print("Use quotes for file names with spaces.")
    sys.exit(1)
outpath = ask_save_location()
generateBatchFile(dirpath, outpath)


    
    
    

