from typing import Dict
from pathlib import Path
import common
import os
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


def analyse_image(file_path: Path) -> Dict[str, str]:
    """Analyses an image using Claude and returns the response.

    Args:
        file_path: Path to the image file.

    Returns:
        The analysis response.
    """
    media_type = get_media_type(file_path)

    # Read and encode the image file in base64
    with open(file_path, 'rb') as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

    response = common.claude_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        system=common.PROMPT,
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
                            "data": img_base64
                        }
                    }
                ]
            }
        ]
    )

    response_dict = response.dict()
    
    return response_dict


def analyse_video(file_path: Path) -> Dict[str, str]:
    # Implement video analysis for Claude
    pass 