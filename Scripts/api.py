from openAiAPI import authenticate, analyseImage, save_to_json
from typing import Dict, List
import common
from exportToCSV4 import export_to_csv
import json

def chatgpt_request(processing_directory: Dict[str, List[str]]) -> None:
    # Authenticate the key to ensure it can be used
    common.client = authenticate("../Private/ClientKeys/chatgpt-api.txt")

    # Process each media in processing dictionary into a separate CSV file for each
    for key in processing_directory:

        for file in processing_directory[key]:
            path_str: str = f"{key}\{file}"

            #TODO: Verbose
            print(f"Sending {path_str} to chatgpt...")
            result: str = analyseImage(path_str)
            print(result)
            save_to_json(result, file)

            with open(f"..\\Output\\{file}.json", 'r') as filename:
                # Load JSON data from the file and convert it to a dictionary
                data = json.load(filename)
                export_to_csv(data)


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