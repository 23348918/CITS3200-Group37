import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
import sys
import common
import cv2
import base64

def ask_save_location(default_filename: str) -> str:
    """Prompt the user to select a location to save a file. If no location is selected, return a default path.

    Args:
        default_filename: The default filename to use if the user does not provide one.
        default_directory: The default directory to use if the user does not provide a location.

    Returns:
        The path selected by the user or the default path if canceled.
    """
    default_directory: str = os.path.join(os.path.dirname(os.path.abspath(__file__)))

    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
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
    file_dict: dict = {}
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