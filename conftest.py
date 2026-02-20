import pytest
from config.config import BASE_URL, HEADERS
from utils.logger import get_logger
from utils.api_client import APIClient


@pytest.fixture(scope="module")
def api_client(request):
    logger = get_logger(request.module.__name__)
    return APIClient(BASE_URL, HEADERS, logger)