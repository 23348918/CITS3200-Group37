import google.generativeai as genai
from PIL import Image

with open("../../Private/ClientKeys/gemini-api.txt", 'r') as file:
    api_key =  file.read().strip()

genai.configure(api_key = api_key)
# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

model = genai.GenerativeModel('gemini-1.5-flash')

img = Image.open("/mnt/c/Users/cohen/OneDrive/uni/2024_2/CITS3200/CITS3200-Group37/Input/Image_Data/Single_Image/test_image.png")

response = model.generate_content(img)
print(response.text)