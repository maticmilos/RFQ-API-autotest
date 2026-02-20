import pytest
from config.config import BASE_URL, HEADERS
from utils.logger import get_logger
from utils.api_client import APIClient


@pytest.fixture
def logger(request):
    return get_logger(request.module.__name__)


@pytest.fixture
def api_client(logger):
    return APIClient(BASE_URL, HEADERS, logger)