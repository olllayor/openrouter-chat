# gemini_client.py
import os
import base64
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Retrieve the Gemini API key from environment variables.  Consider making this configurable in settings.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)



def stream_gemini_completion(messages, model_name="models/gemini-2.0-flash-001"):

    try:
        model = genai.GenerativeModel(model_name)

        # Format the messages for the Gemini API
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if isinstance(content, str):
                gemini_messages.append(
                    {"role": role, "parts": [content]}
                )  # correct format for gemini
            else:  # Assume it's an image
                gemini_messages.append(
                    {"role": role, "parts": [content]}
                )  # correct format for gemini

        # Separate history and prompt
        history = gemini_messages[:-1]
        prompt = gemini_messages[-1]["parts"][0]  # Extract content from parts list

        chat = model.start_chat(history=history)

        response = chat.send_message(prompt, stream=True)
        for chunk in response:
            yield chunk.text

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        yield f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage (for testing purposes)
    example_messages = [
        {"role": "user", "content": "Write a short poem about the ocean."}
    ]

    for token in stream_gemini_completion(example_messages):
        print(token, end="")
