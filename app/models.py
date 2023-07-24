from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ShippingRate(Base):
    __tablename__ = "shipping_rates"

    id = Column(Integer, primary_key=True, index=True)
    starting_country = Column(String, index=True)
    destination_country = Column(String, index=True)
    shipping_channel = Column(String, index=True)
    min_days = Column(Integer)
    max_days = Column(Integer)

    rates = relationship("Rate", back_populates="shipping_rate")


class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, index=True)
    min_weight_kg = Column(Float)
    max_weight_kg = Column(Float)
    per_kg_rate = Column(Float)

    # Define the foreign key relationship to the 'ShippingRate' model
    shipping_rate_id = Column(Integer, ForeignKey("shipping_rates.id"))

    # Define the relationship back to the 'ShippingRate' model
    shipping_rate = relationship("ShippingRate", back_populates="rates")


__all__ = [Base]
