from typing import Dict, Optional, List
from pathlib import Path
import common
import os
import cv2
import base64

def get_media_type(file_path: Path) -> str:
    """Determine the media type based on the file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.png']:
        return 'image/png'
    elif ext in ['.jpg', '.jpeg']:
        return 'image/jpeg'
    elif ext in ['.gif']:
        return 'image/gif'
    elif ext in ['.bmp']:
        return 'image/bmp'
    elif ext in ['.webp']:
        return 'image/webp'
    else:
        raise ValueError(f"Unsupported Claude file extension: {ext}")

def encode_image(image_path: Path) -> str:
    """Encodes an image stored locally into a base64 string."""
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

def encode_video(video_path: Path, frame_rate_divisor: int = 2) -> List[str]:
    """Encodes a video stored locally into an array of base64 strings for frames."""
    images: List[str] = []
    cam = cv2.VideoCapture(str(video_path))
    frame_rate = int(cam.get(cv2.CAP_PROP_FPS) / frame_rate_divisor)  # Take one frame every (FPS / frame_rate_divisor) frames
    count = 0

    while True:
        success, frame = cam.read()
        count += 1
        if success:
            if count % frame_rate == 0:
                success, buffer = cv2.imencode('.jpg', frame)
                if success:
                    images.append(base64.b64encode(buffer).decode('utf-8'))
        else:
            break

    cam.release()
    return images


def analyse_image(file_path: Path) -> Dict[str, str]:
    """Analyses an image using Claude and returns the response.

    Args:
        file_path: Path to the image file.

    Returns:
        The analysis response.
    """
    media_type = get_media_type(file_path)

    # Read and encode the image file in base64
    encoded_image = encode_image(file_path)

    response = common.claude_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        system=common.prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the following image."
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": encoded_image
                        }
                    }
                ]
            }
        ]
    )

    response_dict = response.dict()
    
    return response_dict

def analyse_video(file_path: Path, model: Optional[str] = "claude-3-opus-20240229") -> Dict[str, str]:
    """
    Analyzes a video by breaking it into frames and sending them to Claude.

    Args:
        file_path: Path to the video file.
        model: The Claude model to use. Defaults to "claude-3-opus-20240229".

    Returns:
        A dictionary containing Claude's analysis of the video.
    """
    # Extract frames from the video
    encoded_frames = encode_video(file_path)

    # Prepare the user messages
    model_messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Please analyze the following video and provide an overall description, action, and reasoning."
                }
            ]
        }
    ]

    # Append each encoded frame as an image with the correct media type
    for frame in encoded_frames:
        model_messages[0]["content"].append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",  # Assume all frames are JPEGs
                    "data": frame
                }
            }
        )

    # Send the request to the Claude API
    try:
        response = common.claude_client.messages.create(
            model=model,
            max_tokens=2000,  # Adjust token limit for large number of frames
            system=common.prompt,  # Top-level system parameter
            messages=model_messages  # Only user role messages
        )

        # Convert the response to a dictionary and return
        response_dict = response.dict()
        return response_dict

    except Exception as e:
        print(f"Error analyzing video {file_path}: {e}")
        return {"error": str(e)}
