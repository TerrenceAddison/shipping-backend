from fastapi import APIRouter
from app.controllers import get_shipping_quotes
from app.schemas import Quote, QuoteRequest
from typing import List

router = APIRouter()


@router.get("/")
async def read_root():
    return {"Hello": "World"}


@router.post("/v1/quotes", response_model=List[Quote])
def get_quotes(quote_request: QuoteRequest):
    return get_shipping_quotes(quote_request)
