import requests
import csv

api_url = 

api_key = "sk-cmmL2f-KHMKOpqX8uCazOuyfwFnwiJ30zSAAI3_69sT3BlbkFJeuQ0Bn6z-t343pfxZNWloCTj585gkDZobGtr1LbSgA"

# Send a Get request with the API key in the headers
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(api_url, headers=headers)

# Check if the request was successsful
if response.status_code == 200:
    #Convert the JSON response to a Python object
    data = response.json()

    csv_file_path =

    # Define the headers of the CSV, adjust according to the fields in JSON data
    headers = ['Image_ID','Model','Description','Action','Reasoning']

    # Write data to the CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, filednames=headers)
        writer.writeheader()

        # Initialize Image_ID
        image_id = 1

        # Process each choice and assign a number
        for choice in data['choices']:
            #Extract fields from 'parsed'
            parsed = choice['message'].get('parsed', {})

            # Build the row data to write to the CSV
            row = {
                'Image_ID': image_id,
                'Model': data['model'],
                'Description': parsed.get('description', ''),
                'Action': parsed.get('action', ''),
                'Reasoning': parsed.get('reasoning', '')
            }
            writer.writerow(row)
            image_id += 1 # Increment Image_ID with each loop
    print(f'Data has been successfully exported tp {csv_file_path}')
else:
    print("Failed to retrieve data. Status code:", response.status_code)
