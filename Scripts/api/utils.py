import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from pydantic import BaseModel, create_model
from typing import List, Dict
from common import AnalysisResponse
import common
import cv2
import base64
import os
import sys

def create_dynamic_response_model(custom_str: str) -> BaseModel:
    """
    Creates a dynamic class for custom responses

    Args:
        custom_str (str): String containing each of the custom prompts

    Return:
        BaseModel: custom class of the DynamicAnalysisResponse model
    """

    if custom_str is None:
        return AnalysisResponse
    
    dynamic_fields = {}
    
    lines = custom_str.splitlines()
    for line in lines:
        if ": " in line:
            first_word = line.split(": ")[0].strip()
            dynamic_fields[first_word.lower()] = (str, ...)
    
    DynamicAnalysisResponse = create_model(
        'DynamicAnalysisResponse',  # Name of the new model
        **dynamic_fields,           # Unpack dynamic fields
        __base__=AnalysisResponse    # Inherit from the base class
    )
    
    return DynamicAnalysisResponse

def extract_dynamic_fields(parts: List[str]) -> Dict[str, str]:
        """
        Uses the custom parts of LLM response to append to the response dictionary

        Args:
            parts: custom responses from the LLM model

        Returns:
            dict: containing each of the custom values
        """
        dynamic_fields = {}
        for part in parts[3:]:
            if ": " in part:
                key, value = part.split(": ", 1)
                dynamic_fields[key.strip()] = value.strip()
        return dynamic_fields

def read_customs(file_path: str):
    """
    Reads custom inputs from cli to be used for csv output

    Args:
        file_path (str): The path to the txt file that represents custom inputs.

    Returns:
        str: formatted string of content

    """
    if not file_path.lower().endswith('.txt'):
        raise ValueError("The file must be of type .txt")

    with open(file_path, 'r') as file:
        contents = file.read()
    return contents

def check_file_size(file_path: str) -> bool:
    """
    Checks if the size of the file at the given path exceeds the limit of 99MB.

    Args:
        file_path (str): The path to the file whose size is to be checked.

    Returns:
        bool: True if the file size is within the limit, False if it exceeds the limit.

    """
    batch_file_size = os.path.getsize(file_path)
    file_limit = 99*1024*1024
    if batch_file_size >= file_limit:
        print(f"Processing limit of 99MB reached. Please reduce number of files to be processed.\nTerminating....")
        return False
    return True

def ask_save_location(default_filename: str) -> str:
    """Prompt the user to select a location to save a file. If no location is selected, return a default path.

    Args:
        default_filename: The default filename to use if the user does not provide one.
        default_directory: The default directory to use if the user does not provide a location.

    Returns:
        The path selected by the user or the default path if canceled.
    """
    currentDir = Path(os.path.dirname(os.path.abspath(__file__)))
    default_directory: Path =  currentDir.parents[1]

    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV format", "*.csv"),("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=default_filename,
        initialdir=default_directory,
        title="Select location to save your file"
    )
    
    if not file_path:
        print("Cancelled. Exiting.")
        sys.exit(0)
    return file_path

def get_file_dict(directory_path: Path) -> dict[str, Path]:
    """
    Generate a dictionary of file paths and labels from a directory.

    Args:
        directory_path: The path to the directory containing files.

    Returns:
        A dictionary where keys are file names and values are full file paths.
    """
    # NOTE : for validation and testing
    if not directory_path.is_dir() and not directory_path.is_file():
        raise ValueError(f"The provided path {directory_path} is not a valid path")
    file_dict: dict = {}
    if directory_path.is_file():
        file_dict[directory_path.name] = directory_path
        return file_dict
    else :
        for file_path in directory_path.glob('*'):
            if file_path.is_file() and file_path.suffix in common.VALID_EXTENSIONS:
                file_dict[file_path.name] = file_path
        return file_dict

def get_media_type(file_path: Path) -> str:
    """Determine the media type based on the file extension.
    
    Args:
        file_path: The path to the file.
    
    Returns:
        The media type of the file.
    """
    ext: str = file_path.suffix.lower()
    media_types: dict = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp'
    }
    if ext in media_types:
        return media_types[ext]
    raise ValueError(f"Unsupported file extension: {ext}")

def encode_image(image_path: Path) -> str:
    """Encodes an image stored locally into a base64 string.
    
    Args:
        image_path: The path to the image file.
        
    Returns:
        The base64 encoded image."""
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_video(video_path: Path, frame_rate_divisor: int = 2) -> list[str]:
    """Encodes a video stored locally into an array of base64 strings for frames.
    
    Args:
        video_path: The path to the video file.
        frame_rate_divisor: The divisor to determine the frame rate.
        
    Returns:
        The base64-encoded list of image strings."""
    images: list[str] = []
    cam = cv2.VideoCapture(str(video_path))
    frame_rate: int = int(cam.get(cv2.CAP_PROP_FPS) / frame_rate_divisor)
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        if len(images) % frame_rate == 0:
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                images.append(base64.b64encode(buffer).decode('utf-8'))

    cam.release()
    return images