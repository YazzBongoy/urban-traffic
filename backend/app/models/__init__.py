from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class CameraStatus(StrEnum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class IncidentStatus(StrEnum):
    REPORTED = "reported"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    role: Column = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rtsp_url = Column(String(500), nullable=False)
    status: Column = Column(Enum(CameraStatus), default=CameraStatus.OFFLINE)
    is_360 = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plate_readings = relationship("PlateReading", back_populates="camera")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(20), unique=True, index=True, nullable=False)
    vehicle_type = Column(String(50))
    color = Column(String(30))
    owner_name = Column(String(100))
    owner_phone = Column(String(20))
    is_stolen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plate_readings = relationship("PlateReading", back_populates="vehicle")


class PlateReading(Base):
    __tablename__ = "plate_readings"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    plate_number = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    image_url = Column(String(500))
    direction = Column(String(50))
    speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="plate_readings")
    camera = relationship("Camera", back_populates="plate_readings")


class TrafficZone(Base):
    __tablename__ = "traffic_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    polygon = Column(String(1000))  # GeoJSON polygon
    congestion_level = Column(Float, default=0.0)
    vehicle_count = Column(Integer, default=0)
    average_speed = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)  # accident, breakdown, construction
    description = Column(String(500))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(Integer, default=1)  # 1-5
    status: Column = Column(Enum(IncidentStatus), default=IncidentStatus.REPORTED)
    reported_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)


class TrafficMetric(Base):
    __tablename__ = "traffic_metrics"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("traffic_zones.id"), nullable=False)
    vehicle_count = Column(Integer, default=0)
    average_speed = Column(Float, default=0.0)
    congestion_level = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
