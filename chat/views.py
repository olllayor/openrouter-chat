# views.py
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from PIL import Image  # Import PIL Image to work with images

# Import the Gemini streaming function
from chat.gemini_client import stream_gemini_completion

from .models import Chat, Message, MessageImage
from .utils import convert_image_to_webp

load_dotenv()


def index(request):
    """
    Render the chat interface.
    """
    return render(request, "chat/index.html")


@login_required
@csrf_exempt
def ask_gemini_chat(request):
    """
    Handle chat requests using the Gemini API.
    Accepts both text prompts and image uploads.
    Instead of converting images to binary,
    we load them as PIL Image objects for a faster process.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # Check whether the request is JSON or form-data.
    if request.content_type.startswith("application/json"):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        prompt = data.get("prompt", "")
        model = data.get("model", "models/gemini-2.0-flash-lite-preview-02-05")
        files = []  # JSON requests typically do not include file uploads.
    else:
        prompt = request.POST.get("prompt", "")
        model = request.POST.get("model", "models/gemini-2.0-flash-lite-preview-02-05")
        files = request.FILES.getlist("images")

    # Retrieve or create a chat session for the user.
    user = request.user
    chat_id = request.POST.get("chat_id") or request.session.get("chat_id")
    if chat_id:
        try:
            chat = Chat.objects.get(id=chat_id, user=user)
        except Chat.DoesNotExist:
            chat = Chat.objects.create(user=user, title=f"Chat with Gemini ({model})")
    else:
        chat = Chat.objects.create(user=user, title=f"Chat with Gemini ({model})")
    request.session["chat_id"] = chat.id

    # Build the payload for the Gemini API.
    # Start with the text prompt.
    contents = [{"role": "user", "content": prompt}]

    # Process each uploaded file by converting it to a PIL Image object.
    images = []  # This list will hold PIL Image objects.
    for file in files:
        try:
            # Open the image using Pillow
            img = Image.open(file)
            # Force the image to load into memory
            img.load()
            images.append(img)
            # Reset the file pointer if you need to use the file again (e.g., for saving)
            file.seek(0)
        except Exception as e:
            # If an error occurs, skip this file
            print(f"Failed to open image: {e}")
            continue

    # Append each image object to the payload.
    # The gemini_client will handle these as images.
    for img in images:
        contents.append({"role": "user", "content": img})

    # Save the user's prompt as a text message in the database.
    message = Message.objects.create(chat=chat, sender="user", content=prompt)

    # For record-keeping, convert and save each uploaded image in WEBP format.
    for file in files:
        try:
            webp_image = convert_image_to_webp(file)
            MessageImage.objects.create(message=message, image=webp_image)
        except Exception as e:
            Message.objects.create(
                chat=chat, sender="system", content=f"Failed to process image: {str(e)}"
            )

    # Call the Gemini API using the streaming function.
    token_stream = stream_gemini_completion(contents, model_name=model)

    # Stream tokens back to the client while accumulating the full reply.
    def stream_and_save():
        full_reply = ""
        try:
            for token in token_stream:
                full_reply += token
                yield token  # Yield token immediately for streaming
        except Exception as e:
            full_reply += f"Error: {str(e)}"
            yield f"Error: {str(e)}"
        finally:
            # Save the complete AI response after streaming is done.
            Message.objects.create(chat=chat, sender="ai", content=full_reply)

    return StreamingHttpResponse(stream_and_save(), content_type="text/plain")
