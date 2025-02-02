import json
import os
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Securely load the API key from an environment variable.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

OPENROUTER_CHAT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_ENDPOINT = (
    "https://openrouter.ai/api/v1/models?supported_parameters=free"
)


def index(request):
    """
    Render the chat interface.
    """
    return render(request, "chat/index.html")


def get_models(request):
    """
    Proxy the OpenRouter API /api/v1/models endpoint.
    Filters or additional error handling can be added as needed.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.get(OPENROUTER_MODELS_ENDPOINT, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
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
    except Exception:
        return JsonResponse({"error": "Invalid request body."}, status=400)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,  # Ensure the API supports streaming with this flag.
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            OPENROUTER_CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            stream=True,
            timeout=60,
        )
        print("Status code:", response.status_code)  # Debug log
    except Exception as e:
        print("Error connecting to OpenRouter API:", e)  # Debug log
        return JsonResponse(
            {"error": "Error connecting to OpenRouter API."}, status=500
        )

    def event_stream():
        for line in response.iter_lines(decode_unicode=True):
            # Log the raw line for debugging purposes
            print("Raw line received:", repr(line))
            
            # Skip empty or whitespace-only lines
            if not line or line.strip() == "":
                continue

            # Remove "data: " prefix if it exists
            if line.startswith("data: "):
                line = line[len("data: "):]
            
            # Strip any extraneous whitespace
            line = line.strip()

            try:
                json_data = json.loads(line)
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e, "for line:", repr(line))
                continue

            # Check if the response contains an error key
            if "error" in json_data:
                error_info = json_data["error"]
                error_message = error_info.get("message", "Unknown error")
                # Yield the error message so the UI can display it
                yield f"Error: {error_message}\n"
                # Optionally, you could break here if no further tokens are expected:
                break

            # Process the normal token content
            token = (
                json_data.get("choices", [{}])[0]
                .get("delta", {})
                .get("content", "")
            )
            if token and not token.startswith(": OPENROUTER PROCESSING"):
                yield token + "\n"



    return StreamingHttpResponse(event_stream(), content_type="text/plain")
