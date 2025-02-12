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

model_name = "models/gemini-2.0-flash" # @param ["gemini-1.5-flash-latest","gemini-2.0-flash-lite-preview-02-05","gemini-2.0-flash","gemini-2.0-pro-preview-02-05"] {"allow-input":true}
model_info = genai.get_model(model_name)
print(model_info.input_token_limit, model_info.output_token_limit)