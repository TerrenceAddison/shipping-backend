import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, ShippingRate, Rate
from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    Base.metadata.create_all(bind=engine)


def populate_db():
    with open('data/rates (1).json', 'r') as json_file:
        data = json.load(json_file)

    # create_database() # use database.py to create database

    session = SessionLocal()

    for item in data:
        shipping_rate = ShippingRate(
            starting_country=item["starting_country"],
            destination_country=item["destination_country"],
            shipping_channel=item["shipping_channel"],
            min_days=item["shipping_time_range"]["min_days"],
            max_days=item["shipping_time_range"]["max_days"],
        )

        for rate_data in item["rates"]:
            rate = Rate(
                min_weight_kg=rate_data["min_weight_kg"],
                max_weight_kg=rate_data["max_weight_kg"],
                per_kg_rate=rate_data["per_kg_rate"],
            )
            shipping_rate.rates.append(rate)

        session.add(shipping_rate)

    session.commit()


if __name__ == "__main__":
    populate_db()
