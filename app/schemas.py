from pydantic import BaseModel
from typing import List, Optional


class Box(BaseModel):
    count: int
    weight_kg: float
    length: float
    width: float
    height: float


class ShippingTimeRange(BaseModel):
    min_days: int
    max_days: int


class CostBreakdown(BaseModel):
    shipping_cost: float
    service_fee: float
    oversized_fee: float
    overweight_fee: float


class Quote(BaseModel):
    shipping_channel: str
    total_cost: float
    cost_breakdown: CostBreakdown
    shipping_time_range: ShippingTimeRange


class QuoteRequest(BaseModel):
    starting_country: str
    destination_country: str
    boxes: List[Box]
