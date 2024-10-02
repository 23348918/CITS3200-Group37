from typing import Dict, Optional
import google.generativeai as genai
from pydantic import BaseModel
import common
from PIL import Image
import json
import time
import re



def analyse_image(file_path: str, model_name: Optional[str] = "models/gemini-1.5-pro") -> Dict[str, str]:
    """Analyses an image using the specified model and returns the response.

    Args:
        file_path: Path to the image file.
        model: The model to use for analysis. Defaults to "models/gemini-1.5-pro".

    Returns:
        The analysis response.
    """
    class AnalysisResponse(BaseModel):
        description: str
        reasoning: str
        action: str

    img : Image = Image.open(file_path)
    model = genai.GenerativeModel(model_name=model_name)
    response: Dict[str, str] = model.generate_content(
            [common.PROMPT, img],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema = list[AnalysisResponse])
                )

    # Convert to dict then json string
    json_text = json.loads(response.text)[0]
    response_dic = {
        "model": "models/gemini-1.5-pro",
        "description": json_text["description"],
        "action": json_text["action"],
        "reasoning": json_text["reasoning"]
        }
    return response_dic
    

def analyse_video(file_path: str, model_name: Optional[str] = "models/gemini-1.5-pro") -> Dict[str, str]:
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
    video_file = genai.upload_file(path=file_path)
    while video_file.state.name == "PROCESSING":
        print('Waiting for video to be processed.')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    print(f'Video processing complete: {video_file.uri}')

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)
    model = genai.GenerativeModel(model_name=model_name)
    response: Dict[str, str] = model.generate_content(
            [common.PROMPT, video_file],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema = list[AnalysisResponse],
                max_output_tokens = 300)
                )

    # Convert to dict then json string
    response_dictionary = {"model": model_name}
    for json_section in AnalysisResponse.model_fields.keys():
        match = re.search(f'"{json_section}":\\s*"([^"]*)', response.text)
        response_dictionary[json_section] = match.group(1) if match else ""

    return response_dictionary