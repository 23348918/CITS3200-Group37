# Description: This script is used to create a batch file for the API to process multiple images at once.
# Usage: python3 createBatchFile.py <dirpath | imgpath>
# Example: python3 createBatchFile.py ../../Input/Images
# Example: python3 createBatchFile.py ../../Input/Images/image.jpg
# Output: A batch file named batchfile.jsonl will be created in the Output/BatchFiles directory.
# Note: This code cuts out some images for testing purposes  (every 8th image) to limit the number of images processed at once.

import json
import os
import base64
import sys

PROMPT : str = (
    "You are a road safety visual assistant installed in a car. Your task is to analyze images of road scenes and provide recommendations for safe driving. "
    "The user will provide you with an image or images to analyze."
    "For each image or sub-image, use the template format to explain the following in least words:\n\n"
    "1. Description: Describe what the car is currently doing. Then, describe the objects in the scene in few words, if any, focus on safety hazards, "
    "road signs, traffic lights, road lines/marks, pedestrians, obstacles. \n"
    "2. Recommended Action: In few words, give suggestion as to what action should be taken by the driver. "
    "Also include if driver can change lane, overtake or turn left/right.\n"
    "3. Reason: Explain in few words the reason for recommended action.\n\n"
)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        res = base64.b64encode(image_file.read()).decode('utf-8')
    return res

def createEntry(filepath):
    encodedImage  = encode_image(filepath)
    currentDict = {
        "custom_id": filepath,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": PROMPT,
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze the following image."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encodedImage}"
                            },
                        },
                    ],
                },
            ],
        },
    }
    return currentDict



def getfilepaths(dirPath: str) -> list:
    """
    Recursively get all image file paths from a directory or return a single file path.
    
    :param dirPath: Path to a file or directory
    :return: List of image file paths
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    image_file_paths = []

    # If the path is a file, check its extension and return it if it's an image
    if os.path.isfile(dirPath):
        _, ext = os.path.splitext(dirPath)
        if ext.lower() in image_extensions:
            return [dirPath]
        else:
            return []

    # If the path is a directory, recursively get image file paths
    elif os.path.isdir(dirPath):
        for filename in os.listdir(dirPath):
            file_path = os.path.join(dirPath, filename)
            image_file_paths.extend(getfilepaths(file_path))
    
    return image_file_paths


def generateBatchFile(filePaths: list, outpath: str):
    """
    Generate a batch file containing image file paths.
    
    :param filePaths: List of image file paths
    :param outpath: Output path for the batch file
    """
    if not os.path.exists(outpath):
        os.makedirs(outpath)
        print (f"No path to {outpath}. Creating directory ....")


    outfile = f"{outpath}/batchfile.jsonl"
    with open(outfile, "w") as file: 
        for item in filePaths [::8]:
            entry = createEntry(item)
            json.dump(entry, file)
            file.write("\n")

        if os.path.isfile(outfile):
            print(f"File created in {outfile}.")
        else:
            print("File was not created.")



# ~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~~~~~~~~~ Main ~~~~~~~~~~~~

if len(sys.argv) <2:
    print("Usage: python3 createBatchFile.py <dirpath | imgpath>")
    sys.exit(1)
    
filePaths = getfilepaths(sys.argv[1])
outpath = "../../Output/BatchFiles"
generateBatchFile(filePaths, outpath)


    
    
    

