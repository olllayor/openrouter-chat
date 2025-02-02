# google_api.py
from .base_api import BaseAPI


class GoogleAPI(BaseAPI):
    def chat_completion(self, model, messages, image_url=None, stream=False):
        payload = {"model": model, "messages": messages, "stream": stream}

        if image_url:
            # Ensure content is properly structured
            for message in payload["messages"]:
                if message["role"] == "user":
                    if isinstance(message["content"], str):
                        message["content"] = [
                            {"type": "text", "text": message["content"]}
                        ]
                    message["content"].append(
                        {"type": "image_url", "image_url": {"url": image_url}}
                    )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # e.g. http://localhost:8000
            "X-Title": "Didattica.uz",  # Your application name
        }
        return self._make_request(
            "POST", "", payload=payload, headers=headers, stream=stream
        )
