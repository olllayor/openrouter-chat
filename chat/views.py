import json
import logging
import os
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .google_api import GoogleAPI
from .deepseek_api import DeepSeekAPI

logger = logging.getLogger(__name__)

# Use environment variable for the API key if available
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-default-here")
OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_ENDPOINT = (
    "https://openrouter.ai/api/v1/models?supported_parameters=free"
)


def index(request):
    return render(request, "chat/index.html")


def get_models(request):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(OPENROUTER_MODELS_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.exception("Failed to fetch models.")
        return JsonResponse({"error": "Could not fetch models."}, status=500)

    return JsonResponse(response.json(), safe=False)


@csrf_exempt
def ask_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get("prompt", "")
        model = data.get("model", "")
    except Exception as e:
        logger.exception("Invalid request body")
        return JsonResponse({"error": "Invalid request body."}, status=400)

    # Determine which API to use based on the model
    if "google" in model:
        api = GoogleAPI(OPENROUTER_API_KEY)
    elif "deepseek" in model:
        api = DeepSeekAPI(OPENROUTER_API_KEY)
    else:
        return JsonResponse({"error": "Unsupported model."}, status=400)

    # Prepare the messages payload
    messages = [{"role": "user", "content": prompt}]

    try:
        if "google" in model and "image_url" in data:
            response = api.chat_completion(model, messages, image_url=data["image_url"])
        else:
            response = api.chat_completion(model, messages)

        def event_stream():
            for chunk in response:
                yield f"data: {json.dumps(chunk)}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

    except Exception as e:
        logger.exception("Error connecting to API")
        return JsonResponse({"error": "Error connecting to API."}, status=500)
