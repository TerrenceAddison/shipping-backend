from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database():
    # Base.metadata.drop_all(engine) # for rebuild database
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_database()
