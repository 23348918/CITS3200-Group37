from pathlib import Path
import common
from common import verbose_print
import re

def chatgpt_request(model_name: str, file_path: Path, is_video: bool):
    pass 

def gemini_request(model_name: str, file_path: Path, is_video: bool):
    pass

def claude_request(model_name: str, file_path: Path, is_video: bool):
    pass

def response_to_dictionary(response: str, model_name: str) -> dict[str, str]:
    response_dictionary: dict[str, str] = {"model": model_name}
    for json_section in common.AnalysisResponse.model_fields.keys():
        match: re.Match[str] = re.search(f'"{json_section}":\\s*"([^"]*)', response)
        response_dictionary[json_section] = match.group(1) if match else ""
    return response_dictionary
