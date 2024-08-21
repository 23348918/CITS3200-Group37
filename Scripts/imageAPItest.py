import sys
from openai import OpenAI
import json

if len(sys.argv) < 2:
    print("Usage: python script.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
print(image_path)

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are to analyze the given image(s) and give a decision on what to do in a situation. \
            You are a road safety visual assistant installed in a car which receives images to analyse and process.\
            The user will pass a path to the image to analyse. Sometimes the the image is divided into multiple image, in which case\
            you are to analyse each of the sub image in the image"},
        {
        "role": "user",
        "content": [
            {"type": "text", "text": "For the given image(s) what should the car do"},
            {
            "type": "image_url",
            "image_url": {
                "url": f"{image_path}",
            },
            },
        ],
        }
    ],
    max_tokens=300,
)

# Print the response from OpenAI
# print(response.choices[0]['message']['content'])

try:
    path = "../Output/resultIMG.json"
    with open (path, 'a') as file:
        json.dump(response.to_dict(),file,indent=4)
        file.write ("\n\n\n")
    print(f"Program ran successfully. Check {path} for output")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)

