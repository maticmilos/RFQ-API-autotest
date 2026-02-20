def assert_status_code(response, expected_status: int):
    """Assert response has expected status code."""
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"


def assert_field_exists(response_json: dict, field: str):
    """Check that field exists in response."""
    assert field in response_json, f"Field '{field}' missing in response: {list(response_json.keys())}"


def assert_response_fields(actual_response: dict, expected_fields: dict):
    """Validate response fields match expected values."""
    for field, expected_value in expected_fields.items():
        # Handle special case: message_contains for partial matching
        if field == "message_contains":
            actual_message = actual_response.get("Message", "")
            assert expected_value in actual_message, \
                f"Message should contain '{expected_value}', got: '{actual_message}'"
        else:
            assert field in actual_response, \
                f"Field '{field}' missing in response: {list(actual_response.keys())}"
            actual_value = actual_response.get(field)
            assert actual_value == expected_value, \
                f"Field '{field}': expected '{expected_value}', got '{actual_value}'"


def get_matched_products(response_json: dict) -> list:
    """Extract matched products from nested response structure."""
    all_products = []
    result = response_json.get("result", {})
    matched_items = result.get("matchedItems", [])

    for item in matched_items:
        internal_products = item.get("matchedInternalProducts", [])
        all_products.extend(internal_products)

    return all_products


def assert_percentages_above_threshold(matched_products: list, threshold_decimal: float):
    """
    Check all products meet minimum percentage threshold.

    Note: API uses percentage 0-100, but request threshold is 0.0-1.0 decimal.
    """
    threshold_percentage = threshold_decimal * 100

    for product in matched_products:
        percentage = product.get('percentage', 0)
        product_name = product.get('name', 'Unknown')

        assert percentage >= threshold_percentage, \
            f"Product '{product_name}' has percentage {percentage}% below threshold {threshold_percentage}%"