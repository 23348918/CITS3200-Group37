from pathlib import Path
import common
from common import verbose_print
from PIL import Image
import re
import google.generativeai as genai
import time



def chatgpt_request(file_path: Path):
    pass 

def gemini_request(file_path: Path):
    is_video: bool = file_path.suffix in common.VIDEO_EXTENSIONS
    if is_video:
        file = genai.upload_file(path=file_path)
        while file.state.name == "PROCESSING":
            verbose_print('Waiting for video to be processed.')
            time.sleep(10)
            file = genai.get_file(file.name)
        verbose_print(f'Video processing complete: {file.uri}')
    else:
        file = Image.open(file_path)

    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
    response: dict[str, str] = model.generate_content(
        [common.PROMPT, file],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema = list[common.AnalysisResponse],
            max_output_tokens = 50)
            )
    response_dict = response_to_dictionary(response.text, "models/gemini-1.5-pro")
    response_dict["file_name"] = file_path.name
    return response_dict

def claude_request(is_video: bool):
    pass

def response_to_dictionary(response: str, model_name: str) -> dict[str, str]:
    response_dictionary: dict[str, str] = {"model": model_name}
    for json_section in common.AnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(f'"{json_section}":\\s*"([^"]*)', response)
        response_dictionary[json_section] = match.group(1) if match else ""
    return response_dictionary
