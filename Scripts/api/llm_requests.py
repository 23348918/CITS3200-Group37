from pathlib import Path
import common
from common import verbose_print
from utils import get_media_type, encode_image, encode_video, create_dynamic_response_model
from PIL import Image
import re
import google.generativeai as genai
import time

def chatgpt_request(file_path: Path) -> dict[str, str]:
    """Request for a single file to the ChatGPT API.
    
    Args:
        file_path: Path to the image or video file.
    
    Returns:
        The analysis response as a dictionary."""
    is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
    if is_video:
        encoded_file: list[str] = encode_video(file_path)
    else:
        encoded_file: list[str] = [encode_image(file_path)]
    DynamicAnalysisResponse = create_dynamic_response_model(common.custom_str)
    message: str = common.USER_PROMPT
    for image in encoded_file:
        message["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}"
            }
        })
    messages = [{
                "role": "system",
                "content": common.prompt
            }, message]
    response: str = common.chatgpt_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=DynamicAnalysisResponse
    )
    full_response: dict = response.dict()
    response_dict: dict = full_response['choices'][0]['message']['parsed']
    response_dict["model"] = "gpt-4o-mini"
    response_dict["file_name"] = file_path.name
    return response_dict


def gemini_request(file_path: Path) -> dict[str, str]:
    """Request for a single file to the gemini API.
    
    Args:
        file_path: Path to the image or video file.
    
    Returns:
        The analysis response as a dictionary."""
    is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
    if is_video:
        file = genai.upload_file(path=file_path)
        while file.state.name == "PROCESSING":
            verbose_print('Waiting for video to be processed.')
            time.sleep(common.WAITING_TIMER)
            file = genai.get_file(file.name)
        verbose_print(f'Video processing complete: {file.uri}')
    else:
        file = Image.open(file_path)

    DynamicAnalysisResponse = create_dynamic_response_model(common.custom_str)
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    response: str = model.generate_content(
        [common.prompt, file],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema = list[DynamicAnalysisResponse],
            max_output_tokens = common.MAX_OUTPUT_TOKENS_GEMINI)
            )
    response_dict: dict = response_to_dictionary(response.text, "models/gemini-1.5-pro")
    response_dict["file_name"] = file_path.name
    return response_dict

def claude_request(file_path: Path) -> dict[str, str]:
    """Request for a single file to the Claude API.
    
    Args:
        file_path: Path to the image or video file.
        
    Returns:
        The analysis response as a dictionary."""
    is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
    if is_video:
        media_type: str = "image/jpeg"  # encode video always makes a jpeg
        encoded_file: str = encode_video(file_path)
    else:
        media_type: str = get_media_type(file_path)
        encoded_file: str = [encode_image(file_path)]
    message: str = common.USER_PROMPT
    for image in encoded_file:
        message["content"].append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image
            }
        })
    response: str = common.claude_client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=common.MAX_OUTPUT_TOKENS_CLAUDE,
        system=common.prompt,
        messages=[message]
    )
    full_response: dict = response.dict()
    response_dict: dict = response_to_dictionary(full_response['content'][0]['text'], "models/claude-3-opus-20240229")
    response_dict["file_name"] = file_path.name
    return response_dict

def response_to_dictionary(response: str, model_name: str) -> dict[str, str]:
    """Converts the response from the API to a dictionary. Will contain empty columns if unfinished or errored.
    
    Args:
        response: The response from the API.
        model_name: The name of the model used for the analysis.
        
    Returns:
        The response as a dictionary."""
    response_dictionary: dict[str, str] = {"model": model_name}
    DynamicAnalysisResponse = create_dynamic_response_model(common.custom_str)
    for json_section in DynamicAnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(
        f'"{json_section}":\\s*["]?([^",}}]*)["]?', response)
        response_dictionary[json_section] = match.group(1) if match else ""
    return response_dictionary