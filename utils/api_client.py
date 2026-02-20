import requests
import time
from logging import Logger
from utils.logger import log_request, log_response


class APIClient:
    """API client that logs requests and tracks response times."""

    def __init__(self, base_url: str, headers: dict, logger: Logger):
        self.base_url = base_url
        self.headers = headers
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(headers)

    def post(self, endpoint: str, json_data: dict = None):
        """
        Send POST request.

        Returns:
            tuple: (response object, response_time in seconds)
        """
        url = f"{self.base_url}{endpoint}"

        log_request(self.logger, "POST", url)

        start_time = time.time()
        response = self.session.post(url, json=json_data)
        response_time = time.time() - start_time

        log_response(self.logger, response.status_code, response_time)

        return response, response_time