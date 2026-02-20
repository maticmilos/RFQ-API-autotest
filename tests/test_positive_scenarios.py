import json
import pytest
from config.config import ENDPOINTS
from utils.api_client import APIClient
from utils.helpers import (
    assert_status_code,
    assert_response_fields,
    get_matched_products
)
from utils.logger import get_logger

logger = get_logger(__name__)

# Load test data
with open("tests/test_data.json") as f:
    TEST_DATA = json.load(f)


@pytest.mark.positive
@pytest.mark.severity_medium
@pytest.mark.priority_medium
@pytest.mark.parametrize("case", TEST_DATA["p1_private_label_cases"], ids=lambda c: c["desc"])
def test_p1_private_label_ranking_flag_has_no_effect(api_client: APIClient, case):
    """P1: Private label ranking flag changes product order"""
    logger.info(f"Testing P1: {case['desc']}")

    payload_false = {**case["payload"], "enablePrivateLabelRanking": False}
    logger.info("Testing with enablePrivateLabelRanking=False")
    response_false, _ = api_client.post(ENDPOINTS["upload_free_text"], payload_false)
    assert_status_code(response_false, case["expected_status"])

    response_json_false = response_false.json()
    products_false = get_matched_products(response_json_false)

    payload_true = {**case["payload"], "enablePrivateLabelRanking": True}
    logger.info("Testing with enablePrivateLabelRanking=True")
    response_true, _ = api_client.post(ENDPOINTS["upload_free_text"], payload_true)
    assert_status_code(response_true, case["expected_status"])

    response_json_true = response_true.json()
    products_true = get_matched_products(response_json_true)

    skus_false = [p.get("sku") for p in products_false]
    skus_true = [p.get("sku") for p in products_true]

    logger.info(f"Products order with flag=False: {skus_false}")
    logger.info(f"Products order with flag=True: {skus_true}")

    assert skus_false != skus_true, "Private label ranking flag should change product order"


@pytest.mark.positive
@pytest.mark.severity_high
@pytest.mark.priority_high
@pytest.mark.parametrize("case", TEST_DATA["p2_relevance_cases"], ids=lambda c: c["desc"])
def test_p2_high_percentage_score_for_irrelevant_product(api_client: APIClient, case):
    """P2: Percentage score accuracy for cutting board query"""
    logger.info(f"Testing P2: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)

    if len(matched_products) > 0:
        top_product = matched_products[0]
        product_name = top_product.get("name", "")
        percentage = top_product.get("percentage", 0)

        logger.info(f"Top matched product: '{product_name}' with percentage {percentage}%")

        assert "board" in product_name.lower() or "cutting" in product_name.lower(), \
            f"Top product '{product_name}' with percentage {percentage}% is not relevant to 'Cutting Board'"


@pytest.mark.positive
@pytest.mark.severity_high
@pytest.mark.priority_high
@pytest.mark.parametrize("case", TEST_DATA["p3_url_extraction_cases"], ids=lambda c: c["desc"])
def test_p3_url_upload_returns_wrong_website_content(api_client: APIClient, case):
    """P3: URL content extraction quality"""
    logger.info(f"Testing P3: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_url_html"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)

    logger.info(f"URL extraction returned {len(matched_products)} matched products")

    if len(matched_products) > 0:
        top_product = matched_products[0]
        product_name = top_product.get("name", "").lower()
        percentage = top_product.get("percentage", 0)

        logger.info(f"Top matched product: '{top_product.get('name')}' with percentage {percentage}%")

        is_relevant = any(keyword in product_name for keyword in case["expected_keywords"])

        assert is_relevant, \
            f"URL extracted wrong content - top product '{top_product.get('name')}' not relevant. Expected keywords: {case['expected_keywords']}"
    else:
        logger.warning("No matched products returned - URL extraction may have failed")


@pytest.mark.positive
@pytest.mark.severity_medium
@pytest.mark.priority_medium
@pytest.mark.xfail(strict=False, reason="P4 bug confirmed - API returns inconsistent scores (99% -> 80% -> 99%)")
@pytest.mark.parametrize("case", TEST_DATA["p4_consistency_cases"], ids=lambda c: c["desc"])
def test_p4_percentage_score_inconsistent_for_same_product(api_client: APIClient, case):
    """P4: Percentage score consistency across requests"""
    logger.info(f"Testing P4: {case['desc']}")

    scores = []

    for attempt in range(1, case["attempts"] + 1):
        logger.info(f"Attempt {attempt}/{case['attempts']}: Sending identical request")
        response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
        assert_status_code(response, case["expected_status"])

        response_json = response.json()
        matched_products = get_matched_products(response_json)

        if len(matched_products) > 0:
            score = matched_products[0].get("percentage", 0)
            scores.append(score)
            logger.info(f"Attempt {attempt} percentage: {score}%")

    if len(scores) == case["attempts"]:
        max_score = max(scores)
        min_score = min(scores)
        variation = max_score - min_score

        logger.info(f"Score variation: {variation}% (max: {max_score}%, min: {min_score}%)")

        assert variation <= case["max_variation"], \
            f"Percentage scores should be consistent (±{case['max_variation']}%), got variation of {variation}%: {scores}"


@pytest.mark.positive
@pytest.mark.severity_low
@pytest.mark.priority_low
@pytest.mark.xfail(strict=False, reason="P5 bug confirmed - Missing fields: price, inStock, imageUrl")
@pytest.mark.parametrize("case", TEST_DATA["p5_completeness_cases"], ids=lambda c: c["desc"])
def test_p5_missing_product_key_information_in_results(api_client: APIClient, case):
    """P5: Product information completeness"""
    logger.info(f"Testing P5: {case['desc']}")

    response, _ = api_client.post(ENDPOINTS["upload_free_text"], case["payload"])
    assert_status_code(response, case["expected_status"])

    response_json = response.json()
    matched_products = get_matched_products(response_json)

    if len(matched_products) > 0:
        product = matched_products[0]
        logger.info(f"Product fields present: {list(product.keys())}")

        missing_core_fields = []

        for field in case["required_fields"]:
            if field not in product or not product[field]:
                missing_core_fields.append(field)

        assert len(missing_core_fields) == 0, \
            f"Product missing core fields: {missing_core_fields}. Product has: {list(product.keys())}"

        logger.info(f"Product: {product.get('name')}, SKU: {product.get('sku')}, Vendor: {product.get('vendor', {}).get('name')}")