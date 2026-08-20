from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/statistics")
async def get_statistics(
    period: str = "day",
    db: AsyncSession = Depends(get_db),
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_statistics(period)


@router.get("/predictions")
async def get_predictions(
    hours_ahead: int = 24,
    db: AsyncSession = Depends(get_db),
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.get_predictions(hours_ahead)


@router.get("/reports")
async def generate_report(
    start_date: datetime,
    end_date: datetime,
    db: AsyncSession = Depends(get_db),
):
    analytics_service = AnalyticsService(db)
    return await analytics_service.generate_report(start_date, end_date)
