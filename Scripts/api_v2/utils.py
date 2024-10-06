from typing import List, Dict
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import os
import sys
import common
import cv2
import base64

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

def get_file_dict(directory_path: Path) -> Dict[str, Path]:
    """
    Generate a dictionary of file paths and labels from a directory.

    Args:
        directory_path: The path to the directory containing files.

    Returns:
        A dictionary where keys are file names and values are full file paths.
    """
    file_dict = {}
    for file_path in directory_path.glob('*'):
        if file_path.is_file() and file_path.suffix in common.VALID_EXTENSIONS:
            file_dict[file_path.name] = file_path
    return file_dict
    
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

def get_media_type(file_path: Path) -> str:
    """Determine the media type based on the file extension."""
    ext = file_path.suffix.lower()
    media_types = {
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
    """Encodes an image stored locally into a base64 string."""
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def encode_video(video_path: Path, frame_rate_divisor: int = 2) -> List[str]:
    """Encodes a video stored locally into an array of base64 strings for frames."""
    images: List[str] = []
    cam = cv2.VideoCapture(str(video_path))
    frame_rate = int(cam.get(cv2.CAP_PROP_FPS) / frame_rate_divisor)
    
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