
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.vehicle import PlateReadingResponse, VehicleResponse
from app.services.vehicle import VehicleService

router = APIRouter()


@router.get("/", response_model=list[VehicleResponse])
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    vehicle_service = VehicleService(db)
    return await vehicle_service.get_all(skip=skip, limit=limit)


@router.get("/search/{plate_number}", response_model=list[PlateReadingResponse])
async def search_by_plate(
    plate_number: str,
    db: AsyncSession = Depends(get_db),
):
    vehicle_service = VehicleService(db)
    return await vehicle_service.search_by_plate(plate_number)


@router.get("/{vehicle_id}/history", response_model=list[PlateReadingResponse])
async def get_vehicle_history(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db),
):
    vehicle_service = VehicleService(db)
    return await vehicle_service.get_history(vehicle_id)
