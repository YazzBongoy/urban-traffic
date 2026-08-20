from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Vehicle, PlateReading


class VehicleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        result = await self.db.execute(
            select(Vehicle).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search_by_plate(self, plate_number: str) -> List[PlateReading]:
        result = await self.db.execute(
            select(PlateReading)
            .where(PlateReading.plate_number.ilike(f"%{plate_number}%"))
            .order_by(PlateReading.timestamp.desc())
        )
        return result.scalars().all()

    async def get_history(self, vehicle_id: int) -> List[PlateReading]:
        result = await self.db.execute(
            select(PlateReading)
            .where(PlateReading.vehicle_id == vehicle_id)
            .order_by(PlateReading.timestamp.desc())
        )
        return result.scalars().all()
