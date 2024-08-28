import base64
from typing import Dict, Optional
from pydantic import BaseModel
from openai import OpenAI
import json
from datetime import datetime

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


def analyse_image(client: OpenAI, file_path: str, model: Optional[str] = "gpt-4o-mini") -> Dict[str, str]:
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

    response: Dict[str, str] = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": PROMPT
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
    return response


def save_to_json(response: Dict[str, str]) -> None:
    """Stores the output of LLM to a JSON file.

    Args:
        response: The response data to be saved.
    """
    try:
        output: Dict[str, str] = response
        current_date: datetime = datetime.now().date()
        path: str = f"../Output/{current_date}.json"
        
        with open(path, 'w') as file:
            json.dump(output, file, indent=4)
        
        print(f"Program ran successfully. Check {path} for output.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit(1)
