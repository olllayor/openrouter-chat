# deepseek_api.py
from .base_api import BaseAPI

class DeepSeekAPI(BaseAPI):
    def __init__(self, api_key):
        super().__init__(api_key)

    def chat_completion(self, model, messages):
        payload = {
            "model": model,
            "messages": messages
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        return self._make_request("POST", "", payload=payload, headers=headers)
        