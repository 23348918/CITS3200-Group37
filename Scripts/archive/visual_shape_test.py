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
            "content": [
                {
                "type": "text",
                "text": "You are an assistant. Analyse the image given by \
                the user and respond as to what shape do you think it is"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What’s in this image?"
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

# Print the response from OpenAI
# print(response.choices[0]['message']['content'])

try:
    current_date = datetime.now().date()
    path = f"../Output/image{current_date}.json"
    with open (path, 'w') as file:
        json.dump(response.to_dict(),file,indent=4)
        file.write ("\n\n\n")
    print(f"Program ran successfully. Check {path} for output")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)

