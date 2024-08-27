import requests
import csv

api_url = 
api_key = "sk-cmmL2f-KHMKOpqX8uCazOuyfwFnwiJ30zSAAI3_69sT3BlbkFJeuQ0Bn6z-t343pfxZNWloCTj585gkDZobGtr1LbSgA"

headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    data = response.json()

    csv_file_path =

    
