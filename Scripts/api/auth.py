import sys
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from pathlib import Path
import common
from common import verbose_print

def authenticate(model_name: str) -> object:
    """Authenticates with the appropriate service based on the path to the API key.

    Args:
        auth_path: Path to the file containing the API key.
    """
    script_dir = Path(__file__).parent
    file_path = script_dir / ".." / ".." / "Private" / "ClientKeys" / f"{model_name}-api.txt"
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")
    try:
        with open(file_path, 'r') as file:
            api_key: str = file.read().strip()
    except Exception as e:
        print(f"An unexpected error occurred while reading the API key file: {e}")
        sys.exit(1)

    try:
        match model_name:
            case "chatgpt":
                common.chatgpt_client = OpenAI(api_key=api_key)
            case "claude":
                common.claude_client = Anthropic(api_key=api_key)
            case "gemini":
                genai.configure(api_key=api_key)
            case _:
                print(f"Unrecognized auth path: {file_path}. Please include 'chatgpt' or 'claude' in the file name.")
                sys.exit(1)
    except Exception as e:
        raise Exception(f"Authentication failed: {e} for {model_name}")

    verbose_print(f"Authenicated with {model_name} successfully")