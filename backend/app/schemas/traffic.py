from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TrafficMetricBase(BaseModel):
    zone_id: int
    vehicle_count: int = 0
    average_speed: float = 0.0
    congestion_level: float = 0.0


class TrafficMetricResponse(TrafficMetricBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ZoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    polygon: Optional[str] = None


class ZoneCreate(ZoneBase):
    pass


class ZoneResponse(ZoneBase):
    id: int
    congestion_level: float
    vehicle_count: int
    average_speed: float
    updated_at: datetime

    class Config:
        from_attributes = True


class RealtimeTraffic(BaseModel):
    zones: List[ZoneResponse]
    total_vehicles: int
    average_congestion: float
    timestamp: datetime
