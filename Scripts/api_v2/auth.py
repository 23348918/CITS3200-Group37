import sys
from openai import OpenAI
import os
from anthropic import Anthropic  # Assuming you're using the Anthropic Python client for Claude.
import google.generativeai as genai
from pathlib import Path
import common

def authenticate() -> object:
    """Authenticates with the appropriate service based on the path to the API key.

    Args:
        auth_path: Path to the file containing the API key.

    Returns:
        An authenticated client object for the corresponding LLM (either OpenAI or Claude).
    """
    script_dir = Path(__file__).parent
    file_path = script_dir / ".." / ".." / "Private" / "ClientKeys" / f"{common.model_name}-api.txt"
    if not file_path.exists():
        raise(f"{file_path} does not exist.") 
    try:
        with open(file_path, 'r') as file:
            api_key: str = file.read().strip()
    except Exception as e:
        print(f"An unexpected error occurred while reading the API key file: {e}")
        sys.exit(1)

    # Determine the type of client based on the file name or path.
    if "chatgpt" in file_path.lower():
        try:
            client: OpenAI = OpenAI(api_key=api_key)
            common.chatgpt_client = client
            print("Authenticated with OpenAI (ChatGPT) successfully.")
            return client
        except Exception as e:
            print(f"Failed to authenticate OpenAI: {e}")
            sys.exit(1)
    
    elif "claude" in file_path.lower():
        try:
            client = Anthropic(api_key=api_key)
            print("Authenticated with Claude (Anthropic) successfully.")
            return client
        except Exception as e:
            print(f"Failed to authenticate Claude: {e}")
            sys.exit(1)

    elif "gemini" in file_path.lower():
        try:
            genai.configure(api_key=api_key)
            print("Authenticated with Gemini (Google) successfully.")
            return
        except Exception as e:
            print(f"Failed to authenticate Gemini: {e}")
            sys.exit(1)


    else:
        print(f"Unrecognized auth path: {file_path}. Please include 'chatgpt' or 'claude' in the file name.")
        sys.exit(1)
