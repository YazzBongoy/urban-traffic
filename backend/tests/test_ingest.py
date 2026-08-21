"""Tests du service d'ingestion RNI (get_or_create_vehicle + record_plate_reading)."""

from app.models import Vehicle
from app.services.ingest import get_or_create_vehicle, record_plate_reading


async def test_get_or_create_vehicle_creates_then_reuses(db_sessionmaker):
    async with db_sessionmaker() as db:
        vehicle = await get_or_create_vehicle(db, "AB123CD", vehicle_type="car")
        await db.commit()
        assert vehicle.id is not None
        assert vehicle.plate_number == "AB123CD"

        async with db_sessionmaker() as db2:
            same = await get_or_create_vehicle(db2, "AB123CD")
            assert same.id == vehicle.id

            vehicles = (await db2.execute(Vehicle.__table__.select())).fetchall()
            assert len(vehicles) == 1


async def test_record_plate_reading_links_camera_and_vehicle(db_sessionmaker):
    async with db_sessionmaker() as db:
        vehicle = await get_or_create_vehicle(db, "EF456GH")
        reading = await record_plate_reading(
            db,
            camera_id=1,
            plate_number="EF456GH",
            confidence=0.93,
            vehicle_id=vehicle.id,
        )
        await db.commit()
        assert reading.camera_id == 1
        assert reading.vehicle_id == vehicle.id
        assert reading.plate_number == "EF456GH"
        assert 0.0 <= reading.confidence <= 1.0


async def test_plate_reading_allows_unknown_vehicle(db_sessionmaker):
    async with db_sessionmaker() as db:
        reading = await record_plate_reading(
            db, camera_id=2, plate_number="XYZ999", confidence=0.7
        )
        await db.commit()
        assert reading.vehicle_id is None
