from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ShippingRate(Base):
    __tablename__ = "shipping_rates"

    id = Column(Integer, primary_key=True, index=True)
    starting_country = Column(String, index=True)
    destination_country = Column(String, index=True)
    shipping_channel = Column(String, index=True)
    min_days = Column(Integer)
    max_days = Column(Integer)
    min_weight_kg = Column(Float)
    max_weight_kg = Column(Float)
    per_kg_rate = Column(Float)


__all__ = [Base]
