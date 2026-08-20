from fastapi import APIRouter

from app.api.v1.endpoints import auth, cameras, vehicles, traffic, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["Traffic"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
