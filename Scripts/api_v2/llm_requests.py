from pathlib import Path
import common
from common import verbose_print
from utils import get_media_type, encode_image, encode_video
from PIL import Image
import re
import google.generativeai as genai
import time



def chatgpt_request(file_path: Path) -> dict[str, str]:
    pass 

def gemini_request(file_path: Path) -> dict[str, str]:
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

    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    response: str = model.generate_content(
        [common.PROMPT, file],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema = list[common.AnalysisResponse],
            max_output_tokens = common.MAX_OUTPUT_TOKENS)
            )
    response_dict = response_to_dictionary(response.text, "models/gemini-1.5-pro")
    response_dict["file_name"] = file_path.name
    return response_dict

def claude_request(file_path: Path) -> dict[str, str]:
    is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
    if is_video:
        media_type: str = "image/jpeg"  # encode video always makes a jpeg
        encoded_file = encode_video(file_path)
    else:
        media_type: str = get_media_type(file_path)
        encoded_file = [encode_image(file_path)]
    message = common.USER_PROMPT
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
        max_tokens=common.MAX_OUTPUT_TOKENS,
        system=common.PROMPT,
        messages=[message]
    )
    full_response = response.dict()
    response_dict = response_to_dictionary(full_response['content'][0]['text'], "models/gemini-1.5-pro")
    response_dict["file_name"] = file_path.name
    return response_dict

def response_to_dictionary(response: str, model_name: str) -> dict[str, str]:
    response_dictionary: dict[str, str] = {"model": model_name}
    for json_section in common.AnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(f'"{json_section}":\\s*"([^"]*)', response)
        response_dictionary[json_section] = match.group(1) if match else ""
    return response_dictionary