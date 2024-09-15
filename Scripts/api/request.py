import base64
from typing import Dict, Optional
from pydantic import BaseModel
import common
import cv2

class BatchContentRessponse(BaseModel):
    description: str
    reasoning: str
    action: str


def encode_image(image_path: str) -> str:
    """Encodes an image stored locally into a base64 string before being analysed.

    Args:
        image_path: Path to the image file.

    Returns:
        The base64-encoded image string.
    """
    with open(image_path, "rb") as image_file:
        encoded_image: str = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

def encode_video(video_path: str) -> list[str]:
    """Encodes an video stored locally into an array of base64 strings before being analysed.

    Args:
        image_path: Path to the video file.

    Returns:
        The base64-encoded list of image strings.
    """
    images: list[str] = []
    cam: cv2.VideoCapture = cv2.VideoCapture(video_path)
    captureOnFrames: int = int(cam.get(cv2.CAP_PROP_FPS) / 2) # Gives the spacing between each four frames
    count: int = 0
    while True:
        success,frame = cam.read()
        count += 1
        if success:
            if count % captureOnFrames == 0:
                sucess, buffer = cv2.imencode('.jpg', frame)
                print(f"-- decoding image -- {count}")
                images.append(base64.b64encode(buffer).decode('utf-8'))
        else:
            break
    cam.release()
    return images

def analyse_image(file_path: str, model: Optional[str] = "gpt-4o-mini") -> Dict[str, str]:
    """Analyses an image using the specified model and returns the response.

    Args:
        file_path: Path to the image file.
        model: The model to use for analysis. Defaults to "gpt-4o-mini".

    Returns:
        The analysis response.
    """
    class AnalysisResponse(BaseModel):
        description: str
        reasoning: str
        action: str

    image_path: str = encode_image(file_path)
    response: Dict[str, str] = common.client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": common.PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the following image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_path}"
                        }
                    }
                ]
            }
        ],
        response_format=AnalysisResponse,
    )

    # Convert to dict then json string
    response_dict = response.dict()  # Convert the pydantic model to a dictionary
    return response_dict

def analyse_video(file_path: str, model: Optional[str] = "gpt-4o-mini") -> Dict[str, str]:
    """Analyses an video using the specified model and returns the response.

    Args:
        file_path: Path to the video file.
        model: The model to use for analysis. Defaults to "gpt-4o-mini".

    Returns:
        The analysis response.
    """
    class AnalysisResponse(BaseModel):
        description: str
        reasoning: str
        action: str

    video_path: list[str] = encode_video(file_path)
    model_messages = [
            {
                "role": "system",
                "content": common.PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the following sequence of images."
                    }
                ]
            }
        ]
    for i in video_path:
        model_messages[1]["content"].append(
            {
                "type":"image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{i}"
                }
            }
        )
    response: Dict[str, str] = common.client.beta.chat.completions.parse(
        model=model,
        messages=model_messages,
        response_format=AnalysisResponse,
    )

    # Convert to dict then json string
    response_dict = response.dict()  # Convert the pydantic model to a dictionary
    return response_dict