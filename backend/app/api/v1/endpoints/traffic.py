from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.traffic import TrafficMetricResponse, ZoneResponse
from app.services.traffic import TrafficService

router = APIRouter()


@router.get("/realtime")
async def get_realtime_traffic(db: AsyncSession = Depends(get_db)):
    traffic_service = TrafficService(db)
    return await traffic_service.get_realtime()


@router.get("/history")
async def get_traffic_history(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    zone_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    traffic_service = TrafficService(db)
    return await traffic_service.get_history(start_date, end_date, zone_id)


@router.get("/zones", response_model=List[ZoneResponse])
async def list_zones(db: AsyncSession = Depends(get_db)):
    traffic_service = TrafficService(db)
    return await traffic_service.get_zones()


@router.get("/heatmap")
async def get_heatmap(
    timestamp: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
):
    traffic_service = TrafficService(db)
    return await traffic_service.get_heatmap(timestamp)
