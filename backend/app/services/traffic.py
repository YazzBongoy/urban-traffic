from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import TrafficZone, TrafficMetric


class TrafficService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_realtime(self) -> dict:
        result = await self.db.execute(select(TrafficZone))
        zones = result.scalars().all()
        total_vehicles = sum(z.vehicle_count for z in zones)
        avg_congestion = (
            sum(z.congestion_level for z in zones) / len(zones) if zones else 0
        )
        return {
            "zones": zones,
            "total_vehicles": total_vehicles,
            "average_congestion": avg_congestion,
            "timestamp": datetime.utcnow(),
        }

    async def get_history(
        self,
        start_date: datetime,
        end_date: datetime,
        zone_id: Optional[int] = None,
    ) -> List[TrafficMetric]:
        query = select(TrafficMetric).where(
            TrafficMetric.timestamp.between(start_date, end_date)
        )
        if zone_id:
            query = query.where(TrafficMetric.zone_id == zone_id)
        result = await self.db.execute(query.order_by(TrafficMetric.timestamp))
        return result.scalars().all()

    async def get_zones(self) -> List[TrafficZone]:
        result = await self.db.execute(select(TrafficZone))
        return result.scalars().all()

    async def get_heatmap(self, timestamp: Optional[datetime] = None) -> dict:
        if not timestamp:
            timestamp = datetime.utcnow()
        result = await self.db.execute(
            select(TrafficMetric).where(
                TrafficMetric.timestamp <= timestamp
            ).order_by(TrafficMetric.timestamp.desc()).limit(1000)
        )
        metrics = result.scalars().all()
        return {
            "timestamp": timestamp,
            "data_points": len(metrics),
            "metrics": [
                {
                    "zone_id": m.zone_id,
                    "congestion_level": m.congestion_level,
                    "vehicle_count": m.vehicle_count,
                }
                for m in metrics
            ],
        }
