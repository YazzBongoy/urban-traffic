from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import TrafficMetric


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_statistics(self, period: str = "day") -> dict:
        if period == "day":
            result = await self.db.execute(
                select(
                    func.sum(TrafficMetric.vehicle_count).label("total_vehicles"),
                    func.avg(TrafficMetric.average_speed).label("avg_speed"),
                    func.avg(TrafficMetric.congestion_level).label("avg_congestion"),
                )
            )
        else:
            result = await self.db.execute(
                select(
                    func.sum(TrafficMetric.vehicle_count).label("total_vehicles"),
                    func.avg(TrafficMetric.average_speed).label("avg_speed"),
                    func.avg(TrafficMetric.congestion_level).label("avg_congestion"),
                )
            )
        stats = result.one()
        return {
            "period": period,
            "total_vehicles": stats.total_vehicles or 0,
            "average_speed": round(stats.avg_speed or 0, 2),
            "average_congestion": round(stats.avg_congestion or 0, 2),
        }

    async def get_predictions(self, hours_ahead: int = 24) -> dict:
        return {
            "hours_ahead": hours_ahead,
            "predictions": [],
            "model": "LSTM (to be trained)",
        }

    async def generate_report(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        result = await self.db.execute(
            select(TrafficMetric).where(
                TrafficMetric.timestamp.between(start_date, end_date)
            )
        )
        metrics = result.scalars().all()
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_records": len(metrics),
            "summary": {
                "total_vehicles": sum(m.vehicle_count for m in metrics),
                "avg_speed": (
                    sum(m.average_speed for m in metrics) / len(metrics)
                    if metrics
                    else 0
                ),
                "avg_congestion": (
                    sum(m.congestion_level for m in metrics) / len(metrics)
                    if metrics
                    else 0
                ),
            },
        }
