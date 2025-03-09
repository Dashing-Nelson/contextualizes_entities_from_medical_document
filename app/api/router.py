from fastapi import APIRouter

from app.api.v1 import router as v1_router

api_router = APIRouter(prefix="/api", tags=["api"])

api_router.include_router(v1_router, tags=["v1", "extract"])
