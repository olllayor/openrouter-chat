# views.py
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from PIL import Image  # For processing images

# Import Gemini streaming function and other clients as needed.
from chat.gemini_client import stream_gemini_completion

from .models import Chat, Message, MessageImage

# Import our image conversion utility and Pillow Image.
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
    Handle chat requests using the Gemini API, accepting both text prompts and images.

    The view:
      - Accepts either JSON or multipart/form-data requests.
      - Extracts a text prompt.
      - Optionally processes uploaded images (converting to PIL objects for the API and
        to WEBP for storage).
      - Builds a contents list starting with the prompt string and any images.
      - Calls the Gemini API using a streaming response.
      - Saves the user's prompt and uploaded images, as well as the full AI response.

    Model used: models/gemini-2.0-flash-lite-preview-02-05
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    # Determine if the request is JSON or multipart form-data.
    if request.content_type.startswith("application/json"):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        prompt = data.get("prompt", "")
        model = data.get("model", "models/gemini-2.0-flash-lite-preview-02-05")
        # JSON requests typically won't include file uploads.
        files = []
    else:
        # For multipart form-data, get the text fields from POST and files from FILES.
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
    # The first element is the prompt (a string).
    # Subsequent elements are PIL Image objects for each uploaded image.
    contents = [{"role": "user", "content": prompt}]
    pil_images = []
    for file in files:
        try:
            # Open the image as a PIL Image.
            pil_img = Image.open(file)
            pil_images.append(pil_img)
        except Exception:
            # Log or handle the error as needed; here we simply skip the image.
            continue
    # Append all valid images to the contents.
    for img in pil_images:
        contents.append({"role": "user", "content": img})

    # Save the user prompt in the database.
    message = Message.objects.create(chat=chat, sender="user", content=prompt)

    # For every uploaded file, convert to WEBP and store for record.
    for file in files:
        try:
            webp_image = convert_image_to_webp(file)
            MessageImage.objects.create(message=message, image=webp_image)
        except Exception as e:
            Message.objects.create(
                chat=chat, sender="system", content=f"Failed to process image: {str(e)}"
            )

    # Call the Gemini API using our streaming function.
    # We assume that stream_gemini_completion accepts a list of contents including text and images.
    token_stream = stream_gemini_completion(contents, model_name=model)

    # Stream the tokens as they arrive and accumulate the full reply.
    def stream_and_save():
        full_reply = ""
        try:
            for token in token_stream:
                if "Error:" in token:
                    full_reply += token
                    yield token
                    break
                full_reply += token
                yield token
        except Exception as e:
            full_reply += f"Error: {str(e)}"
            yield f"Error: {str(e)}"
        finally:
            # Save the full AI response after streaming completes.
            Message.objects.create(chat=chat, sender="ai", content=full_reply)

    return StreamingHttpResponse(stream_and_save(), content_type="text/plain")
