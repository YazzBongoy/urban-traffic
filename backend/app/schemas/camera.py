from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class CameraBase(BaseModel):
    name: str
    location: str
    latitude: float
    longitude: float
    rtsp_url: str
    is_360: bool = True


class CameraCreate(CameraBase):
    pass


class CameraResponse(CameraBase):
    id: int
    status: CameraStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
