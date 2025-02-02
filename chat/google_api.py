# google_api.py
from .base_api import BaseAPI

class GoogleAPI(BaseAPI):
    def __init__(self, api_key):
        super().__init__(api_key)

    def chat_completion(self, model, messages, image_url=None):
        payload = {
            "model": model,
            "messages": messages
        }

        if image_url:
            payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        return self._make_request("POST", "", payload=payload, headers=headers)