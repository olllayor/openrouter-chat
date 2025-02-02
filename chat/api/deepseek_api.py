from .base_api import BaseAPI


class DeepSeekAPI(BaseAPI):
    def chat_completion(self, model, messages, stream=False):
        payload = {"model": model, "messages": messages, "stream": stream}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Didattica.uz",
        }
        return self._make_request(
            "POST", "", payload=payload, headers=headers, stream=stream
        )
