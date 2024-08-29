import pandas as pd

def export_to_csv(data: str) -> None:
    rows = []
    for index, choice in enumerate(data['choices'], start=1):
        parsed = choice['message']['parsed']
        row = {
            'Image_ID': index,
            'Model': data['model'],
            'Description': parsed['description'],
            'Action': parsed['action'],
            'Reasoning': parsed['reasoning']
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    csv_file_path = '..\output.csv'

    df.to_csv(csv_file_path, index=False)

    print(f'Data has been successfully exported to {csv_file_path}')
