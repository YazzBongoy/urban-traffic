from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VehicleBase(BaseModel):
    plate_number: str
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleResponse(VehicleBase):
    id: int
    is_stolen: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlateReadingBase(BaseModel):
    plate_number: str
    confidence: float
    direction: Optional[str] = None
    speed: Optional[float] = None


class PlateReadingCreate(PlateReadingBase):
    vehicle_id: Optional[int] = None
    camera_id: int
    image_url: Optional[str] = None


class PlateReadingResponse(PlateReadingBase):
    id: int
    vehicle_id: Optional[int]
    camera_id: int
    image_url: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True
