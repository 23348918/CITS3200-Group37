import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from pydantic import BaseModel, create_model
from typing import List, Dict
from common import AnalysisResponse, verbose_print
import common
import cv2
import base64
import os
import sys


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
        print("Processing limit of 99MB reached. Please reduce number of files to be processed.\nTerminating....")
        return False
    return True

def ask_save_location(default_filename: str):
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
    
    root.attributes("-topmost", True)
    root.update()
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV format", "*.csv"),("Text files", "*.txt"), ("All files", "*.*")],
        initialfile=default_filename,
        initialdir=default_directory,
        title="Select location to save your file"
    )
    
    if not file_path:
        return False
    return file_path

def get_file_dict(directory_path: Path) -> dict[str, Path]:
    """
    Generate a dictionary of file paths and labels from a directory recursively.

    Args:
        directory_path: The path to the directory containing files.

    Returns:
        A dictionary where keys are file names and values are full file paths.
    """
    # NOTE: for validation and testing
    if not directory_path.is_dir() and not directory_path.is_file():
        raise ValueError(f"The provided path {directory_path} is not a valid path")
    
    file_dict: dict[str, Path] = {}

    if directory_path.is_file():
        file_dict[directory_path.name] = directory_path
        return file_dict

    # Iterate through all items in the directory
    for file_path in directory_path.glob('*'):
        if file_path.is_file(): 
            if file_path.suffix in common.VALID_EXTENSIONS:
                file_dict[file_path.name] = file_path
            else:
                verbose_print(f"Skipping {file_path.name} as it is not a valid file type.")
        elif file_path.is_dir():
            # Recursive call for subdirectories
            subdir_files = get_file_dict(file_path)
            file_dict.update(subdir_files)

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
    
    # Get the video's original frame rate
    fps = cam.get(cv2.CAP_PROP_FPS)
    
    # Calculate how many frames to skip for capturing frames every second
    frame_skip = int(fps)  # Capture every frame at 1 second intervals
    
    count = 0
    while True:
        success, frame = cam.read()
        if not success:
            break
        if count % frame_skip == 0:  # Capture frame every second
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                images.append(base64.b64encode(buffer).decode('utf-8'))
        count += 1

    cam.release()

    return images
    
