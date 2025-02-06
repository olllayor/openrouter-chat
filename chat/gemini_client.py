# gemini_client.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Retrieve the Gemini API key from environment variables.  Consider making this configurable in settings.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)


def stream_gemini_completion(messages, model_name="gemini-1.5-pro-latest"):
    """
    Streams the completion from the Google Gemini API.

    Args:
        messages: A list of dictionaries, where each dictionary represents a message
                  in the conversation.  Each dictionary should have 'role' and 'content' keys.
                  Example:
                  [
                      {'role': 'user', 'content': 'Hello'},
                      {'role': 'model', 'content': 'Hi there!'},
                      {'role': 'user', 'content': 'How are you?'}
                  ]
        model_name: The name of the Gemini model to use.  Defaults to "gemini-1.5-pro-latest".

    Yields:
        str: Individual tokens from the Gemini API's streaming response.

    Raises:
        Exception: If there's an error communicating with the Gemini API.
    """
    try:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=messages[:-1])  # Initialize the chat with history. Last message is the prompt
        response = chat.send_message(messages[-1]["content"], stream=True) # Send only last message
        
        for chunk in response:
            yield chunk.text  # Yield each token (chunk) from the response

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        yield f"Error: {str(e)}" # Yield an error message to the stream.  Crucial for client-side error handling.



if __name__ == '__main__':
    # Example usage (for testing purposes)
    example_messages = [
        {'role': 'user', 'content': 'Write a short poem about the ocean.'}
    ]

    for token in stream_gemini_completion(example_messages):
        print(token, end="") # prints the streaming content