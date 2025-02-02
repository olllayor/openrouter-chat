import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)  # Securely fetch API key from environment variable
BASE_URL = "https://openrouter.ai/api/v1"


def get_available_models():
    """Fetches the list of available models from OpenRouter API."""
    response = requests.get(f"{BASE_URL}/models")
    return [model["id"] for model in response.json()["data"]]


def get_free_available_models():
    response = requests.get(f"{BASE_URL}/models?supported_parameters=free")
    return [model["id"] for model in response.json()["data"]]


def send_message_to_openrouter(model_name, messages):
    """Sends messages to the OpenRouter API and returns the streaming response."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model_name,
        "messages": messages,
        "stream": True,  # Enable streaming
    }
    print(data)
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True,
        )
        print(response.json())

        response.raise_for_status()
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to OpenRouter API: {e}")
        return None
