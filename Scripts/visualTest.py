from datetime import datetime
import sys
from openai import OpenAI
import json
import base64


# need to encode image to base64 before passing to API since it is stored locally
# otherwise image links doesnt need to be encoded
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# check argvalues passed to the program
if len(sys.argv) < 2:
    print("Usage: python script.py <image_path>")
    sys.exit(1)

image_path = encode_image(sys.argv[1])


try:
    # with open("../Private/LanceKeys/APIKey.txt", 'r') as file:
    with open("../Private/ClientKeys/chatgpt-api.txt", 'r') as file:
        apiKey = file.read().strip()

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)



client = OpenAI(
    api_key=apiKey
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system", 
            "content": (
                "You are to analyze the given image(s) and give a decision on what to do in a situation. "
                "You are a road safety visual assistant installed in a car, which receives images to analyze and process. "
                "The user will pass a path to the image to analyze. Sometimes the image is divided into multiple images, in which case "
                "you are to analyze each of the sub-images in the image.\n\n"
                "Describe objects in the scene with extra attention to safety hazards. "
                "Describe potential dangers in the scene. "
                "Describe what action you would take as a driver. "
                "Describe the reason for the action."
            )
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyse the image"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_path}"

                    }
                }
            ]
        }
    ],    
    max_tokens=300,
)



try:
    current_date = datetime.now().date()
    path = f"../Output/{current_date}.json"
    with open (path, 'w') as file:
        json.dump(response.to_dict(),file,indent=4)
        file.write ("\n\n\n")
    print(f"Program ran successfully. Check {path} for output")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)
