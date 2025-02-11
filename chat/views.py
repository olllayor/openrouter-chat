# views.py
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from PIL import Image  # Still useful for processing images if needed

# Removed base64 import since it’s not used anymore
# from chat.gemini_client import stream_gemini_completion
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
    Handle chat requests using the Gemini API, accepting both text prompts and images.
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
        files = []  # JSON requests typically won't include file uploads.
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
    # The first element is the prompt as a text message.
    contents = [{"role": "user", "content": prompt}]
    image_binaries = []  # This list will hold raw binary data for each valid image.
    for file in files:
        try:
            # Read the file's raw binary content.
            binary_data = file.read()
            # Reset the file pointer so it can be used later for saving the image.
            file.seek(0)
            image_binaries.append(binary_data)
        except Exception:
            # If an error occurs, skip this file.
            continue
    # Append binary image data to the contents.
    for img_data in image_binaries:
        contents.append({"role": "user", "content": img_data})

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
    token_stream = stream_gemini_completion(contents, model_name=model)

    # Stream tokens and save the complete reply.
    def stream_and_save():
        full_reply = ""
        try:
            # For every token received from the API, append and yield it.
            for token in token_stream:
                full_reply += token
                yield token  # Stream token without breaking on errors.
        except Exception as e:
            # If an exception occurs, include the error in the full reply.
            full_reply += f"Error: {str(e)}"
            yield f"Error: {str(e)}"
        finally:
            # Save the full AI response after streaming completes.
            Message.objects.create(chat=chat, sender="ai", content=full_reply)


    return StreamingHttpResponse(stream_and_save(), content_type="text/plain")
