import google.generativeai as genai
from pydantic import BaseModel
from PIL import Image
import common
import json

with open("../../Private/ClientKeys/gemini-api.txt", 'r') as file:
    api_key =  file.read().strip()

genai.configure(api_key = api_key)

img = Image.open("/mnt/c/Users/cohen/OneDrive/uni/2024_2/CITS3200/CITS3200-Group37/Input/Image_Data/Single_Image/test_image.png")


# Define your schema
class AnalysisResponse(BaseModel):
    description: str
    reasoning: str
    action: str

# Call the API
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

result = model.generate_content(
  [common.PROMPT, img],
  generation_config=genai.GenerationConfig(response_mime_type="application/json",
                                           response_schema = list[AnalysisResponse],
                                           max_output_tokens=300))

# print(result)
# print(result.text)
json_text = json.loads(result.text)[0]
print(json_text)
print(type(json_text))
for key, value in json_text.items():
    print(key, value)
print(json_text["description"])
gemini_dict = {
    "model": "models/gemini-1.5-pro",
    "Description": json_text["description"],
    "Action": json_text["action"],
    "Reason": json_text["reasoning"]
    }
print(type(gemini_dict))
print(gemini_dict)