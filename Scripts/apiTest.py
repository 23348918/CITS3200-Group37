
from openai import OpenAI
import json

# for org ID
try:
    with open("../Private/LanceKeys/orgID.txt", 'r') as file:
        orgID = file.read().strip()

    with open("../Private/LanceKeys/projID.txt", 'r') as file:
        projID = file.read().strip()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)


client = OpenAI(
  organization=orgID,
  project=projID,
)

completion = client.chat.completions.create(
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
    path = "../Output/result.json"
    with open (path, 'a') as file:
        json.dump(completion.to_dict(),file,indent=4)
        file.write ("\n\n\n")
    print(f"Program ran successfully. Check {path} for output")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit(1)


