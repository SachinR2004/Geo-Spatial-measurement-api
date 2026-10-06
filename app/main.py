from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.router import router
from app.db.base import Base
from app.db.session import engine
import app.models.uploaded_file  # Registers uploaded_file in Base.metadata
import app.models.measurement    # Registers measurement in Base.metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Creates tables in PostgreSQL on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Geospatial Measurement API",
    description="Backend service for processing geospatial files and calculating measurements.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(
    router,
    prefix="/api",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}