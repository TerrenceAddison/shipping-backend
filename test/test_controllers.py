import pytest
from app.schemas import QuoteRequest, Quote, Box
from app.controllers import get_shipping_quotes, calculate_shipping_cost
from app.constants import MAX_BOX_WEIGHT, MAX_BOX_DIMENSION, MAX_BOX_WEIGHT_INDIA, MAX_BOX_DIMENSION_VIETNAM, SERVICE_FEE_CHINA, OVERWEIGHT_FEE, OVERSIZED_FEE
from fastapi import HTTPException
from pydantic import ValidationError


def test_calculate_shipping_cost():
    # Test case 1: Box weight > 30 and box dimension < 120 (and more than 1 box)
    box = Box(count=2, weight_kg=40.0, length=1.0,
              width=1.0, height=1.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "China")
    assert total_weight == 80.0
    assert oversized_fee == 0.0
    assert overweight_fee == OVERWEIGHT_FEE * 2

    # Test case 2: Box weight > 30 and box dimension > 120 (and more than 1 box)
    box = Box(count=3, weight_kg=40.0, length=1.0,
              width=130.0, height=140.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "China")
    assert total_weight == 120.0
    assert oversized_fee == OVERSIZED_FEE * 3
    assert overweight_fee == OVERWEIGHT_FEE * 3

    # Test case 3: Box weight < 30 and box dimension < 120
    box = Box(count=1, weight_kg=20.0, length=1.0, width=1.0, height=1.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "China")
    assert total_weight == 20.0
    assert oversized_fee == 0.0
    assert overweight_fee == 0.0

    # Test case 4: Box weight < 30 and box dimension > 120
    box = Box(count=1, weight_kg=20.0, length=130.0, width=1.0, height=1.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "China")
    assert total_weight == 20.0
    assert oversized_fee == OVERSIZED_FEE
    assert overweight_fee == 0.0

    # Test case 5: Volumetric weight > gross Weight (with oversized and overweight fees)
    box = Box(count=1, weight_kg=40.0, length=10.0, width=1000.0, height=30.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "China")
    assert total_weight == 50.0
    assert oversized_fee == OVERSIZED_FEE
    assert overweight_fee == OVERWEIGHT_FEE

    # Test case 6: Shipment from India overweight for more than 15kg, oversized is normal
    box = Box(count=2, weight_kg=20.0, length=1.0, width=130.0, height=1.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "India")
    assert total_weight == 40.0
    assert oversized_fee == OVERSIZED_FEE * 2
    assert overweight_fee == OVERWEIGHT_FEE * 2

    # Test case 7: Shipment from vietnam oversized for more than 70cm, overweight is normal
    box = Box(count=2, weight_kg=40.0, length=1.0, width=80.0, height=1.0)
    total_weight, oversized_fee, overweight_fee = calculate_shipping_cost(
        box, "Vietnam")
    assert total_weight == 80.0
    assert oversized_fee == OVERSIZED_FEE * 2
    assert overweight_fee == OVERWEIGHT_FEE * 2


def test_get_shipping_quotes():
    # Test case 1: Quote with gross weight, show  both air and ocean options available + complete data check
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=2, weight_kg=100, length=1.0, width=1.0, height=1.0),
            Box(count=1, weight_kg=100, length=5.0, width=5.0, height=5.0),
        ],
    )
    quotes = get_shipping_quotes(quote_request)
    assert len(quotes) == 2
    assert quotes[0].shipping_channel == "air"
    assert quotes[0].total_cost == 1590.0
    assert quotes[0].cost_breakdown.shipping_cost == 1050.0
    assert quotes[0].cost_breakdown.service_fee == 300.0
    assert quotes[0].cost_breakdown.oversized_fee == 0.0
    assert quotes[0].cost_breakdown.overweight_fee == 240.0
    assert quotes[0].shipping_time_range.min_days == 15
    assert quotes[0].shipping_time_range.max_days == 20

    assert quotes[1].shipping_channel == "ocean"
    assert quotes[1].total_cost == 840.0
    assert quotes[1].cost_breakdown.shipping_cost == 300.0
    assert quotes[1].cost_breakdown.service_fee == 300.0
    assert quotes[1].cost_breakdown.oversized_fee == 0.0
    assert quotes[1].cost_breakdown.overweight_fee == 240.0
    assert quotes[1].shipping_time_range.min_days == 45
    assert quotes[1].shipping_time_range.max_days == 50

    # Test case 2: Quote with volumetric weight, show both air and ocean options
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=1, weight_kg=25.0, length=110.0, width=100.0, height=90.0),
        ],
    )
    quotes = get_shipping_quotes(quote_request)
    assert len(quotes) == 2
    assert quotes[0].shipping_channel == "air"
    assert quotes[1].shipping_channel == "ocean"

    # Test case 3: Quote with gross weight, should only show air option available
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=1, weight_kg=25.0, length=1.0, width=1.0, height=1.0),
        ],
    )
    quotes = get_shipping_quotes(quote_request)
    assert len(quotes) == 1
    assert quotes[0].shipping_channel == "air"

    # Test case 3: Quote with volumetric weight, should only show air option available
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=1, weight_kg=1.0, length=100.0, width=60.0, height=10.0),
        ],
    )
    quotes = get_shipping_quotes(quote_request)
    assert len(quotes) == 1
    assert quotes[0].shipping_channel == "air"

    # Test case 4: Quote with correct service fee and shipping time
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=1, weight_kg=200, length=1.0, width=1.0, height=1.0),
        ],
    )
    quotes = get_shipping_quotes(quote_request)
    assert len(quotes) == 2
    assert quotes[0].shipping_channel == "air"
    assert quotes[1].shipping_channel == "ocean"
    assert quotes[0].cost_breakdown.service_fee == 300.0
    assert quotes[1].cost_breakdown.service_fee == 300.0

    assert quotes[0].shipping_time_range.min_days == 15
    assert quotes[0].shipping_time_range.max_days == 20
    assert quotes[1].shipping_time_range.min_days == 45
    assert quotes[1].shipping_time_range.max_days == 50

    # Test case 5: quote error because of no weight range
    quote_request = QuoteRequest(
        starting_country="China",
        destination_country="USA",
        boxes=[
            Box(count=1, weight_kg=100000.0,
                length=100.0, width=60.0, height=10.0),
        ],
    )
    with pytest.raises(HTTPException) as exc_info:
        quotes = get_shipping_quotes(quote_request)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
