# gemini_client.py
import os
from io import BytesIO
import google.generativeai as genai
from PIL import Image  # Import PIL Image if needed for type checking
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)


def stream_gemini_completion(messages, model_name="models/gemini-2.0-flash-001"):
    try:
        model = genai.GenerativeModel(model_name)
        gemini_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            # Handle text strings
            if isinstance(content, str):
                gemini_messages.append({"role": role, "parts": [content]})
            # Handle PIL Image objects
            elif isinstance(content, Image.Image):
                gemini_messages.append({"role": role, "parts": [content]})
            # Fallback conversion (if needed)
            else:
                gemini_messages.append({"role": role, "parts": [str(content)]})

        # Separate history and prompt.
        history = gemini_messages[:-1]
        prompt = gemini_messages[-1]["parts"][0]

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
