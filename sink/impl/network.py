from sink.base.sink import Sink
from model.model import Result
import logging
import requests

logger = logging.getLogger(__name__)


URL = "http://localhost:5000/api"


def send_post_request(url, data):
    """
    Send a POST request to a specified URL with the provided data.

    :param url: The endpoint to send the POST request to.
    :param data: The data to include in the POST request body. Can be a dictionary or JSON-serializable object.
    :return: The response object from the POST request.
    """
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred: {e}")
        return None


class Network(Sink):
    def __init__(self, name: str, params: dict = {}):
        super().__init__(name)
        self._parameters = params
        self._url = params.get("url", URL)
        logger.info("Network initialized")


    def put(self, result: Result) -> None:
        detection_str = [det.to_json() for det in result.detections]
        send_post_request(URL, {"detections": detection_str})


    def release(self):
        logger.info("Network released")


    def init(self):
        logger.info("Network initialized")



# Example usage:
# url = "https://example.com/api"
# data = {"key": "value"}
# response = send_post_request(url, data)
# if response:
#     print("Response status code:", response.status_code)
#     print("Response body:", response.json())
