import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.models import Base
from app.database import create_database
from populate_db import populate_db

app = FastAPI()

# Include the router from app.routes.py
app.include_router(router)

# Configure CORS (Cross-Origin Resource Sharing) to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    create_database()
    populate_db()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)
