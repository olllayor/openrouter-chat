# base_api.py
import requests
import logging

logger = logging.getLogger(__name__)


class BaseAPI:
    def __init__(
        self, api_key, base_url="https://openrouter.ai/api/v1/chat/completions"
    ):
        if not api_key:
            raise ValueError("API key must be provided")
        self.api_key = api_key
        self.base_url = base_url

    def _make_request(self, method, endpoint, payload=None, headers=None, stream=False):
        url = f"{self.base_url}{endpoint}"
        try:
            with requests.Session() as session:
                response = session.request(
                    method,
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30,
                    stream=stream,
                )
                response.raise_for_status()

                if stream:
                    for line in response.iter_lines():
                        if line:
                            # Remove the extra 'data:' prefix if present
                            decoded_line = line.decode("utf-8")
                            if decoded_line.startswith("data: data:"):
                                decoded_line = decoded_line.replace(
                                    "data: data:", "data:"
                                )
                            yield decoded_line
                else:
                    return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise
