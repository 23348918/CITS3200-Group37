import base64
from typing import Dict, Optional
from pydantic import BaseModel
import common


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
    response: Dict[str, str] = common.chatgpt_client.beta.chat.completions.parse(
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
