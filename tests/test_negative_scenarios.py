"""
Negative test scenarios - API errors and failures
Tests for bugs N1-N5
"""
import json
import pytest
from config.config import ENDPOINTS
from utils.api_client import APIClient
from utils.helpers import (
    assert_status_code,
    assert_response_fields,
    get_matched_products,
    assert_percentages_above_threshold
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Load test data
with open("tests/test_data.json") as f:
    TEST_DATA = json.load(f)


@pytest.mark.negative
@pytest.mark.severity_medium
@pytest.mark.priority_high
@pytest.mark.parametrize("case", TEST_DATA["n1_empty_text_cases"], ids=lambda c: c["desc"])
def test_n1_empty_text_returns_400_correctly(api_client: APIClient, case):
    """N1: Empty text validation - API correctly returns 400"""
    logger.info(f"Testing N1: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])

    logger.info(f"Validating response: Expected {case['expected_status']}, got {response.status_code}")
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    assert_response_fields(response_json, case["expected_response"])


@pytest.mark.negative
@pytest.mark.severity_high
@pytest.mark.priority_high
@pytest.mark.parametrize("case", TEST_DATA["n2_invalid_url_cases"], ids=lambda c: c["desc"])
def test_n2_invalid_url_returns_400_correctly(api_client: APIClient, case):
    """N2: Invalid URL validation - API correctly returns 400"""
    logger.info(f"Testing N2: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_url_html"], case["payload"])

    logger.info(f"Validating response: Expected {case['expected_status']}, got {response.status_code}")
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    assert_response_fields(response_json, case["expected_response"])


@pytest.mark.negative
@pytest.mark.severity_high
@pytest.mark.priority_medium
@pytest.mark.parametrize("case", TEST_DATA["n3_threshold_cases"], ids=lambda c: c["desc"])
def test_n3_threshold_parameter_ignored(api_client: APIClient, case):
    """N3: Threshold parameter filtering - returns products below threshold"""
    logger.info(f"Testing N3: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)
    logger.info(f"Received {len(matched_products)} products, validating threshold >= {case['payload']['threshold']*100}%")

    assert_percentages_above_threshold(matched_products, case["payload"]["threshold"])


@pytest.mark.negative
@pytest.mark.severity_medium
@pytest.mark.priority_medium
@pytest.mark.parametrize("case", TEST_DATA["n4_topk_cases"], ids=lambda c: c["desc"])
def test_n4_topk_parameter_not_respected(api_client: APIClient, case):
    """N4: topK parameter handling"""
    logger.info(f"Testing N4: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)

    logger.info(f"{case['desc']} returned {len(matched_products)} products (expected {case['expected_max']})")
    assert len(matched_products) <= case["expected_max"], \
        f"{case['desc']} should return at most {case['expected_max']} products, got {len(matched_products)}"


@pytest.mark.negative
@pytest.mark.severity_low
@pytest.mark.priority_low
@pytest.mark.parametrize("case", TEST_DATA["n5_special_chars_cases"], ids=lambda c: c["desc"])
def test_n5_special_characters_break_product_matching(api_client: APIClient, case):
    """N5: Special characters handling"""
    logger.info(f"Testing N5: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)

    logger.info(f"Received {len(matched_products)} products (expected > 0)")
    assert len(matched_products) > 0, f"Special characters ({case['desc']}) should not prevent matching"