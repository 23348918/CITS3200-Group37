import requests
import csv

# Replace with your actual API endpoint
api_url = "YOUR_API_URL"

# Send a GET request
response = requests.get(api_url)

# Check if the request was successful
if response.status_code == 200:
    # Convert the JSON response to a Python object
    data = response.json()
    
    # Replace with the actual path where you want to save the CSV file
    csv_file_path = 'YOUR_CSV_FILE_PATH'

    # Define the headers (column names) of the CSV, adjust according to the fields in your JSON data
    headers = ['id', 'created', 'model', 'completion_tokens', 'prompt_tokens', 'total_tokens', 'Image_ID']

    # Write data to the CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        # Assuming each response has a unique image ID, this is just an example, adjust according to your data structure
        image_id = 1  # You need a method to generate or retrieve image IDs
        for choice in data['choices']:
            # Since we assume each response corresponds to an image ID, we need to manage these IDs here
            row = {
                'id': data['id'],
                'created': data['created'],
                'model': data['model'],
                'completion_tokens': data['usage']['completion_tokens'],
                'prompt_tokens': data['usage']['prompt_tokens'],
                'total_tokens': data['usage']['total_tokens'],
                'Image_ID': image_id  # Assuming the image ID increments or changes according to some rule each loop
            }
            writer.writerow(row)
            image_id += 1  # Adjust the increment logic according to your needs

    print(f'Data has been successfully exported to {csv_file_path}')
else:
    print("Failed to retrieve data. Status code:", response.status_code)

