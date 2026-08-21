from fastapi import APIRouter, Depends

from app.api.v1.endpoints import analytics, auth, cameras, traffic, vehicles
from app.services.auth import get_current_user, require_operator

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(
    cameras.router,
    prefix="/cameras",
    tags=["Cameras"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["Vehicles"],
    dependencies=[Depends(require_operator)],
)
api_router.include_router(
    traffic.router,
    prefix="/traffic",
    tags=["Traffic"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_current_user)],
)
