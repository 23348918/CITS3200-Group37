from pathlib import Path
import common
from common import verbose_print
from PIL import Image
import re
import google.generativeai as genai
import time

def chatgpt_request(model_name: str, file_path: Path, is_video: bool):
    pass 

def gemini_request(model_name: str, file_path: Path, is_video: bool):
    if is_video:
        file = genai.upload_file(path=file_path)
        while file.state.name == "PROCESSING":
            verbose_print('Waiting for video to be processed.')
            time.sleep(10)
            file = genai.get_file(file.name)
        verbose_print(f'Video processing complete: {file.uri}')
    else:
        file = Image.open(file_path)

    model = genai.GenerativeModel(model_name=model_name)
    response: dict[str, str] = model.generate_content(
        [common.PROMPT, file],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema = list[common.AnalysisResponse],
            max_output_tokens = 300)
            )
    response_dict = response_to_dictionary(response.text, model_name)
    return [response_dict]

def claude_request(model_name: str, file_path: Path, is_video: bool):
    pass

def response_to_dictionary(response: str, model_name: str) -> dict[str, str]:
    response_dictionary: dict[str, str] = {"model": model_name}
    for json_section in common.AnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(f'"{json_section}":\\s*"([^"]*)', response)
        response_dictionary[json_section] = match.group(1) if match else ""
    return response_dictionary
