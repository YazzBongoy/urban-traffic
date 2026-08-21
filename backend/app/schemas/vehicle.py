from datetime import datetime

from pydantic import BaseModel


class VehicleBase(BaseModel):
    plate_number: str
    vehicle_type: str | None = None
    color: str | None = None
    owner_name: str | None = None
    owner_phone: str | None = None


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
    direction: str | None = None
    speed: float | None = None


class PlateReadingCreate(PlateReadingBase):
    vehicle_id: int | None = None
    camera_id: int
    image_url: str | None = None


class PlateReadingResponse(PlateReadingBase):
    id: int
    vehicle_id: int | None
    camera_id: int
    image_url: str | None
    timestamp: datetime

    class Config:
        from_attributes = True
