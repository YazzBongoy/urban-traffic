from datetime import datetime

from pydantic import BaseModel


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
    description: str | None = None
    polygon: str | None = None


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
    zones: list[ZoneResponse]
    total_vehicles: int
    average_congestion: float
    timestamp: datetime
