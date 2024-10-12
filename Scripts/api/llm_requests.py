from pathlib import Path
import common
from common import verbose_print
from utils import get_media_type, encode_image, encode_video
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
    print("Prompt: ", common.prompt)
    print("AnalysisResponse model fields: ", common.AnalysisResponse.model_fields.keys())
    response: str = common.chatgpt_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        response_format=common.AnalysisResponse
    )
    print(response)
    full_response: dict = response.dict()
    response_dict: dict = full_response['choices'][0]['message']['parsed']
    response_dict["model"] = "gpt-4o-mini"
    response_dict["file_name"] = file_path.name
    print(response_dict)
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

    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    safe = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

    response: str = model.generate_content(
        [file, common.prompt],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.3,
            # I have actually no clue but for some reason response_schema breaks everything
            # response_schema = common.AnalysisResponse,
            max_output_tokens = common.MAX_OUTPUT_TOKENS_GEMINI),
            safety_settings=safe
            )
    response_dict: dict = response_to_dictionary(response.text, "gemini-1.5-pro")
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
    for json_section in common.AnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(
            rf'(?i)["\']?({json_section})["\']?[:]\s*([\[]?(?:["\']?[\w ]*["\']?[,]?[ ]*)+[\]]?)', response)
        match_output: str = match.group(2) if match else ""
        if match_output[-1] == ",":
            match_output = match_output[:-1]
        match_output = match_output.replace('"', '').replace("'", '').replace('[', '').replace(']', '').strip()
        response_dictionary[json_section] = match_output
    return response_dictionary