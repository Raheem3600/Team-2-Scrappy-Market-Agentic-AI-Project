from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.metadata import router as metadata_router
from app.routers.query import router as query_router

app = FastAPI(title="ScrappyMarket Data API", version="0.1.0")

app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(query_router)