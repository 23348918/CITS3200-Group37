from datetime import datetime
from openai import OpenAI
import json
import base64




# for org ID
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
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "What is an AI"
        }
    ]
)



# output of chatgpt to json
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


