import json
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.uploadedfile import InMemoryUploadedFile
import traceback
from django.shortcuts import render
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import base64
import io

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the generative model
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")


def index(request):
    """Renders the chat interface."""
    return render(request, "chat/index.html")


@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Processes user input and returns AI-generated responses."""
    # Parse the incoming JSON data
    data = json.loads(request.body)
    msg = data.get("chat", "")
    chat_history = data.get("history", [])

    # Start a chat session with the model
    chat_session = model.start_chat(history=chat_history)

    # Send message and get response
    response = chat_session.send_message(msg)

    return JsonResponse({"text": response.text})


# Modified scale_image function
def scale_image(image_file, max_width=512):
    """Scale image maintaining aspect ratio with format preservation"""
    try:
        image = Image.open(image_file)
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background

        scale_factor = max_width / image.width
        new_height = int(image.height * scale_factor)
        
        resized_image = image.resize((max_width, new_height), Image.LANCZOS)
        
        buffer = io.BytesIO()
        format = 'JPEG' if image.format == 'JPEG' else 'PNG'
        resized_image.save(buffer, format=format, quality=85)
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode("utf-8"), f"image/{format.lower()}"
    except Exception as e:
        raise ValueError(f"Image processing error: {str(e)}")

@csrf_exempt
@require_http_methods(["POST"])
def stream(request):
    """Streams AI responses for real-time chat interactions with image support."""

    def generate():
        try:
            msg = request.POST.get("chat", "")
            chat_history = json.loads(request.POST.get("history", "[]"))

            content_parts = []

            # Handle image if present
            if "image" in request.FILES:
                try:
                    image_file = request.FILES["image"]
                    base64_image = scale_image(image_file)
                    
                    content_parts.append({
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    })
                except Exception as img_error:
                    yield f"data: Error processing image: {str(img_error)}\n\n"
                    return

            # Add text prompt after image (as recommended in the docs)
            content_parts.append(msg)

            # Generate response
            response = model.generate_content(content_parts, stream=True)

            # In your stream view
            for chunk in response:
                if chunk.text:
                    # Proper SSE format with double newline
                    yield f"data: {json.dumps(chunk.text)}\n\n"

        except Exception as e:
            yield f"data: Error processing request: {str(e)}\n\n"

    return StreamingHttpResponse(generate(), content_type="text/event-stream")
