# openrouter.py

import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

# Define the OpenRouter API endpoint
OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"


def stream_openrouter_response(payload, headers, chat, prompt, save_messages_callback):
    """
    Sends a POST request to the OpenRouter API with streaming enabled.
    Yields tokens as they are received.

    :param payload: The JSON payload to send in the POST request.
    :param headers: The headers for the POST request.
    :param chat: The chat object (used for saving messages).
    :param prompt: The original prompt (used for saving messages).
    :param save_messages_callback: A callback function to save messages.
    """
    ai_response_content = ""
    try:
        response = requests.post(
            OPENROUTER_CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60,
        )

        # If the response status code is not 200, handle the error.
        if response.status_code != 200:
            error_msg = f"OpenRouter API error: {response.status_code}"
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and "error" in error_data:
                    error_msg = error_data["error"].get("message", error_msg)
            except Exception:
                pass
            save_messages_callback(chat, prompt, error_msg, is_error=True)
            yield f"Error: {error_msg}\n"
            return

        # Stream the response from OpenRouter.
        for line in response.iter_lines(decode_unicode=True):
            if not line or line.isspace():
                continue

            # Skip [DONE] messages
            if line == "data: [DONE]" or line == "[DONE]":
                continue

            # Remove the 'data: ' prefix if present
            if line.startswith("data: "):
                line = line[6:]

            try:
                json_data = json.loads(line)
                if "error" in json_data:
                    error_msg = json_data["error"].get("message", "Unknown error")
                    save_messages_callback(chat, prompt, error_msg, is_error=True)
                    yield f"Error: {error_msg}\n"
                    return

                # Extract the token from the response data
                token = (
                    json_data.get("choices", [{}])[0]
                    .get("delta", {})
                    .get("content", "")
                )
                if token:
                    ai_response_content += token
                    yield token + "\n"
            except json.JSONDecodeError:
                # Log if there is a JSON decoding error (but ignore DONE messages)
                if "[DONE]" not in line:
                    print(f"Failed to decode JSON: {line}")
                continue

    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        save_messages_callback(chat, prompt, error_msg, is_error=True)
        yield f"Error: {error_msg}\n"
        return

    # Save the full AI response after streaming is complete.
    if ai_response_content:
        save_messages_callback(chat, prompt, ai_response_content)
