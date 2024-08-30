from auth import authenticate
from request import analyse_image
from typing import Dict, List
import common as common
from utils import to_csv
import json

# json_data = """{{
#     "id": "chatcmpl-A0SgKCSXp2pLUCJvaNUAphkPd0qe0",
#     "choices": [
#         {
#             "finish_reason": "stop",
#             "index": 0,
#             "logprobs": null,
#             "message": {
#                 "content": "{\"description\":\"The car appears to be approaching an intersection with road markings indicating a crosswalk. There\u2019s a public parking sign directing to the left and concrete barriers limiting the road space. Nearby buildings suggest a developed urban area.\",\"reasoning\":\"The clear direction of the parking sign indicates an option for the driver. The presence of barriers suggests caution is needed to navigate the area safely without entering restricted zones.\",\"action\":\"Make a left turn towards the public parking area.\"}",
#                 "refusal": null,
#                 "role": "assistant",
#                 "tool_calls": [],
#                 "parsed": {
#                     "description": "The car appears to be approaching an intersection with road markings indicating a crosswalk. There\u2019s a public parking sign directing to the left and concrete barriers limiting the road space. Nearby buildings suggest a developed urban area.",
#                     "reasoning": "The clear direction of the parking sign indicates an option for the driver. The presence of barriers suggests caution is needed to navigate the area safely without entering restricted zones.",
#                     "action": "Make a left turn towards the public parking area."
#                 }
#             }
#         }
#     ],
#     "created": 1724673616,
#     "model": "gpt-4o-mini-2024-07-18",
#     "object": "chat.completion",
#     "system_fingerprint": "fp_507c9469a1",
#     "usage": {
#         "completion_tokens": 93,
#         "prompt_tokens": 37073,
#         "total_tokens": 37166
#     }
# }
# }
# """

def chatgpt_request(processing_directory: Dict[str, List[str]]) -> None:
    # Authenticate the key to ensure it can be used
    common.client = authenticate("../../Private/ClientKeys/chatgpt-api.txt")

    # Process each media in processing dictionary into a separate CSV file for each
    for key in processing_directory:

        for file in processing_directory[key]:
            path_str: str = f"{key}\{file}"

            #TODO: Verbose
            print(f"Sending {path_str} to chatgpt...")
            result_dict: Dict[str, str] = analyse_image(path_str)
            print(result_dict)
            to_csv(result_dict)

        # Output to given file csv
            
    print("DONE")
    pass


def gemini_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass


def claude_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass


def llama_request(processing_directory: Dict[str, List[str]]) -> None:
    print("DONE")
    pass