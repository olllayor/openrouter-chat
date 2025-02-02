# base_api.py
import requests
import logging

logger = logging.getLogger(__name__)

class BaseAPI:
    def __init__(self, api_key, base_url="https://openrouter.ai/api/v1/chat/completions"):
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(self, method, endpoint, payload=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(f"Error making request to {url}: {e}")
            raise