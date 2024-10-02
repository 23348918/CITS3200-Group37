import sys
from openai import OpenAI
import os
from anthropic import Anthropic  # Assuming you're using the Anthropic Python client for Claude.

def authenticate(auth_path: str) -> object:
    """Authenticates with the appropriate service based on the path to the API key.

    Args:
        auth_path: Path to the file containing the API key.

    Returns:
        An authenticated client object for the corresponding LLM (either OpenAI or Claude).
    """
    try:
        with open(auth_path, 'r') as file:
            api_key: str = file.read().strip()
    except Exception as e:
        print(f"An unexpected error occurred while reading the API key file: {e}")
        sys.exit(1)

    # Determine the type of client based on the file name or path.
    if "chatgpt" in auth_path.lower():
        try:
            client: OpenAI = OpenAI(api_key=api_key)
            print("Authenticated with OpenAI (ChatGPT) successfully.")
            return client
        except Exception as e:
            print(f"Failed to authenticate OpenAI: {e}")
            sys.exit(1)
    
    elif "claude" in auth_path.lower():
        try:
            client = Anthropic(api_key=api_key)
            print("Authenticated with Claude (Anthropic) successfully.")
            return client
        except Exception as e:
            print(f"Failed to authenticate Claude: {e}")
            sys.exit(1)

    else:
        print(f"Unrecognized auth path: {auth_path}. Please include 'chatgpt' or 'claude' in the file name.")
        sys.exit(1)
