import sys
from openai import OpenAI


def authenticate(auth_path: str) -> OpenAI:
    """Authenticates with the OpenAI service using an API key read from a file.

    Args:
        auth_path: Path to the file containing the API key.

    Returns:
        An authenticated OpenAI client object.
    """
    try:
        with open(auth_path, 'r') as file:
            api_key: str = file.read().strip()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    
    client: OpenAI = OpenAI(api_key=api_key)
    return client