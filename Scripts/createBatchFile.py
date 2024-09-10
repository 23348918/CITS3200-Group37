# To use this program just pass a directory or an image path
import json
import os
import base64
import sys


def createEntry(filepath):
    currentDict = {
        "custom_id": filepath,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. "
                        "The user will provide you with an image or images to analyze."
                        "For each image or sub-image, use the template format to explain the following in least words:"
                        "Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, road signs, traffic lights, road lines/marks, pedestrians, obstacles. "
                        "Recommended Action: In few words, give suggestion as to what action should be taken by the driver. Also include if driver can change lane, overtake or turn left/right."
                        "Reason: Explain in few words the reason for recommended action."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the following image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{filepath}"
                            },
                        },
                    ],
                },
            ],
        },
    }
    return currentDict


def getfilepaths(dirPath:str):      
    image_file_paths = []
    
    if os.path.isfile(dirPath):
        return [dirPath]
    
    for filename in os.listdir(dirPath):
        file_path = os.path.join(dirPath, filename)

        image_file_paths.append(file_path)
    return image_file_paths


# ~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~
filePaths = getfilepaths(sys.argv[1])


    
    
    

