from app.schemas import QuoteRequest, Quote, Box
from app.schemas import ShippingTimeRange, CostBreakdown
from app.models import ShippingRate, Rate
from app.database import SessionLocal
from typing import List, Tuple


def calculate_shipping_cost(box: Box, starting_country: str) -> Tuple[float, float, float]:
    session = SessionLocal()
    # Calculate gross weight and volumetric weight
    gross_weight = box.count * box.weight_kg
    volumetric_weight = (box.length * box.width *
                         box.height * box.count) / 6000

    # Choose the chargeable weight as the larger of gross weight and volumetric weight
    chargeable_weight = max(gross_weight, volumetric_weight)

    # Calculate the shipping cost based on chargeable weight and per-kg rate
    total_weight = chargeable_weight

    oversized_fee = 0.0
    overweight_fee = 0.0

    if box.weight_kg > 30:
        overweight_fee += (80.0 * box.count)
    if max(box.length, box.width, box.height) > 120:
        oversized_fee += (100.0 * box.count)

    # Apply country-specific fees
    if starting_country == "India" and box.weight_kg >= 15 and overweight_fee == 0.0:
        overweight_fee += (100.0 * box.count)
    elif starting_country == "Vietnam" and max(box.length, box.width, box.height) > 70:
        oversized_fee += (100.0 * box.count)

    session.close()
    return total_weight, oversized_fee, overweight_fee


def get_shipping_quotes(quote_request: QuoteRequest) -> List[Quote]:
    session = SessionLocal()
    quotes = []
    total_shipping_weight = 0.0
    service_fee = 0.0
    total_oversized_fee = 0.0
    total_overweight_fee = 0.0

    # service fee
    if quote_request.starting_country == "China":
        service_fee += 300.0

    weight_and_costs = [calculate_shipping_cost(
        box, quote_request.starting_country, ) for box in quote_request.boxes]
    weight_list, oversized_fee_list, overweight_fee_list = zip(
        *weight_and_costs)
    total_shipping_weight = sum(weight_list)
    total_oversized_fee = sum(oversized_fee_list)
    total_overweight_fee = sum(overweight_fee_list)

    shipping_rate = (
        session.query(ShippingRate)
        .filter(
            ShippingRate.starting_country == quote_request.starting_country,
            ShippingRate.destination_country == quote_request.destination_country,
            ShippingRate.shipping_channel == "air"
        )
        .first()
    )
    # rates are min exclusive, max inclusive
    per_kg_rate = (
        session.query(Rate)
        .filter(
            Rate.shipping_rate_id == shipping_rate.id,
            Rate.min_weight_kg < total_shipping_weight,
            Rate.max_weight_kg >= total_shipping_weight
        )
        .first()
    )

    shipping_cost_air = total_shipping_weight * per_kg_rate.per_kg_rate

    total_cost_air = shipping_cost_air + service_fee + \
        total_overweight_fee + total_oversized_fee

    shipping_time_range_air = ShippingTimeRange(
        min_days=shipping_rate.min_days, max_days=shipping_rate.max_days)
    cost_breakdown_air = CostBreakdown(
        shipping_cost=shipping_cost_air,
        service_fee=service_fee,
        oversized_fee=total_oversized_fee,
        overweight_fee=total_overweight_fee
    )

    quote = Quote(
        shipping_channel="air",
        total_cost=total_cost_air,
        cost_breakdown=cost_breakdown_air,
        shipping_time_range=shipping_time_range_air
    )
    quotes.append(quote)

    # check ocean fare
    shipping_rate_ocean = (
        session.query(ShippingRate)
        .filter(
            ShippingRate.starting_country == quote_request.starting_country,
            ShippingRate.destination_country == quote_request.destination_country,
            ShippingRate.shipping_channel == "ocean"
        )
        .first()
    )

    per_kg_rate_ocean = (
        session.query(Rate)
        .filter(
            Rate.shipping_rate_id == shipping_rate_ocean.id,
            Rate.min_weight_kg < total_shipping_weight,
            Rate.max_weight_kg >= total_shipping_weight
        )
        .first()
    )

    if per_kg_rate_ocean:
        shipping_cost_ocean = total_shipping_weight * per_kg_rate_ocean.per_kg_rate
        total_cost_ocean = shipping_cost_ocean + service_fee + \
            total_overweight_fee + total_oversized_fee
        shipping_time_range_ocean = ShippingTimeRange(
            min_days=shipping_rate_ocean.min_days, max_days=shipping_rate_ocean.max_days)
        cost_breakdown_ocean = CostBreakdown(
            shipping_cost=shipping_cost_ocean,
            service_fee=service_fee,
            oversized_fee=total_oversized_fee,
            overweight_fee=total_overweight_fee
        )
        quote_ocean = Quote(
            shipping_channel="ocean",
            total_cost=total_cost_ocean,
            cost_breakdown=cost_breakdown_ocean,
            shipping_time_range=shipping_time_range_ocean,
        )
        quotes.append(quote_ocean)

    session.close()
    return quotes
