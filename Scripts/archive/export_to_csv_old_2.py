import pandas as pd

# Test input
json_data = [
    {
    "id": "chatcmpl-9yybcErqZxlHotGCEJArahLXpGUQR",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": None,
            "message": {
                "content": "content 1",
                "refusal": None,
                "role": "assistant"
            }
        }
    ],
    "created": 1724319676,
    "model": "gpt-3.5-turbo-0125",
    "object": "chat.completion",
    "system_fingerprint": None,
    "usage": {
        "completion_tokens": 65,
        "prompt_tokens": 21,
        "total_tokens": 86
    }
},
    {
    "id": "chatcmpl-9yybcErqZxlHotGCEJArahLXpGUQR",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "logprobs": None,
            "message": {
                "content": "content 2",
                "refusal": None,
                "role": "assistant"
            }
        }
    ],
    "created": 1724319676,
    "model": "gpt-3.5-turbo-0125",
    "object": "chat.completion",
    "system_fingerprint": None,
    "usage": {
        "completion_tokens": 65,
        "prompt_tokens": 21,
        "total_tokens": 86
    }
}

]
image_ids = [1, 2]

if len(image_ids) != len(json_data):
    raise ValueError("The number of image IDs must match the number of JSON objects.")

content_list = [entry['choices'][0]['message']['content'] for entry in json_data]

df = pd.DataFrame({
    'image_id': image_ids,
    'content': content_list
})

df.to_csv('output.csv', index=False)
print("CSV file created successfully.")