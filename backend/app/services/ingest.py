"""Persistance des passages de véhicules détectés par le pipeline vision (Phase 2 — RNI)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlateReading, Vehicle


async def get_or_create_vehicle(
    db: AsyncSession,
    plate_number: str,
    vehicle_type: str | None = None,
) -> Vehicle:
    result = await db.execute(select(Vehicle).where(Vehicle.plate_number == plate_number))
    vehicle = result.scalar_one_or_none()
    if vehicle is not None:
        if vehicle_type and not vehicle.vehicle_type:
            vehicle.vehicle_type = vehicle_type
            await db.flush()
        return vehicle
    vehicle = Vehicle(plate_number=plate_number, vehicle_type=vehicle_type)
    db.add(vehicle)
    await db.flush()
    return vehicle


async def record_plate_reading(
    db: AsyncSession,
    camera_id: int,
    plate_number: str,
    confidence: float,
    vehicle_id: int | None = None,
) -> PlateReading:
    reading = PlateReading(
        camera_id=camera_id,
        plate_number=plate_number,
        confidence=confidence,
        vehicle_id=vehicle_id,
    )
    db.add(reading)
    await db.flush()
    return reading
