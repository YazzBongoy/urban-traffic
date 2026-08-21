#!/usr/bin/env python3
"""Seed de donnees de demonstration pour le dashboard Urban Traffic (Kinshasa, RDC).

Genere des donnees realistes et deterministes (random standard, pas de Faker) :
  - 6 TrafficZones (communes de Kinshasa, polygones GeoJSON)
  - 8 Cameras (statuts varies, flux RTSP fictifs)
  - 15 Vehicles (plaques format RDC) + PlateReadings sur 48 h
  - TrafficMetrics toutes les 15 min sur 24 h pour chaque zone
  - 3 Incidents (accident, congestion, panne feux)

Idempotent : les lignes de demo precedentes sont detectees par conventions
(zones connues, rtsp_url prefixe, plaques du pool, coordonnees d'incidents)
puis remplacees. Les utilisateurs ne sont jamais touches.

Usage :
    backend/.venv/bin/python scripts/seed_dev_data.py [--db URL] [--clear]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import random
import sys
import types
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Contournement : backend/app/core/config.py leve une ValidationError si le
# .env contient des cles inconnues (extra_forbidden). Le seed n'a besoin que
# d'importer les modeles ; on fournit donc un settings minimal sans lire .env.
_config_stub = types.ModuleType("app.core.config")
_config_stub.settings = SimpleNamespace(DATABASE_URL="sqlite+aiosqlite:///")
sys.modules.setdefault("app.core.config", _config_stub)

from app.models import (
    Camera,
    CameraStatus,
    Incident,
    IncidentStatus,
    PlateReading,
    TrafficMetric,
    TrafficZone,
    Vehicle,
)
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DEFAULT_DB_URL = "sqlite+aiosqlite:////home/ascatsarl/urban-traffic/backend/urban_traffic.db"
RTSP_PREFIX = "rtsp://demo.trafic-kinshasa.local/"

random.seed(2026)


def utcnow() -> datetime:
    """UTC naive, coherent avec les defaults datetime.utcnow des modeles."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Jeux de donnees deterministes
# ---------------------------------------------------------------------------

DEMO_ZONES = [
    # (nom, description, lat, lng, capacite vehicules, vitesse libre km/h)
    ("Gombe", "Centre d'affaires : Boulevard du 30 Juin, ministères et ambassades", -4.3032, 15.2915, 950, 50),
    ("Kintambo", "Carrefour Kintambo et axe vers le Mont-Ngafula", -4.3348, 15.2687, 620, 45),
    ("Limete", "Zone industrielle et rond-point Limete (7e rue)", -4.3680, 15.3305, 540, 40),
    ("Ngaliema", "Axes Gombe-Ngaliema, avenue de la Democratie", -4.3215, 15.2465, 700, 48),
    ("Masina", "Corridor est, boulevard Lumumba vers l'aeroport", -4.3735, 15.3960, 480, 55),
    ("Lingwala", "Rond-point Gambela et marches populaires", -4.3402, 15.3195, 520, 38),
]

CAMERA_SPOTS = [
    # (zone, nom, emplacement, lat, lng, statut, is_360)
    ("Gombe", "CAM-GOM-01", "Boulevard du 30 Juin / Avenue de la Justice", -4.3036, 15.2928, CameraStatus.ONLINE, True),
    ("Gombe", "CAM-GOM-02", "Rond-point Gecoco (ex-Forescom)", -4.3060, 15.2965, CameraStatus.ONLINE, False),
    ("Kintambo", "CAM-KIN-01", "Carrefour Kintambo / Boulevard Sendwe", -4.3352, 15.2690, CameraStatus.ONLINE, True),
    ("Limete", "CAM-LIM-01", "Rond-point Limete 7e Rue", -4.3675, 15.3312, CameraStatus.MAINTENANCE, True),
    ("Ngaliema", "CAM-NGA-01", "Avenue de la Democratie / Route Matadi", -4.3208, 15.2450, CameraStatus.ONLINE, False),
    ("Masina", "CAM-MAS-01", "Boulevard Lumumba / Rond-point Masina", -4.3740, 15.3955, CameraStatus.OFFLINE, True),
    ("Masina", "CAM-MAS-02", "Avenue de la Liberte quartier Kimbanseke est", -4.3902, 15.4110, CameraStatus.OFFLINE, False),
    ("Lingwala", "CAM-LGW-01", "Rond-point Gambela / Avenue Kabasele", -4.3410, 15.3202, CameraStatus.ONLINE, True),
]

VEHICLE_FLEET = [
    # (plaque, type, couleur, proprietaire, telephone, vole)
    ("CD 12345 KD", "Toyota Hiace (bus)", "Blanc", "Jean-Pierre Mbala", "+243 815 243 118", False),
    ("CD 23456 KD", "Moto-taxi", "Bleu", "Patrick Ilunga", "+243 822 764 902", False),
    ("CD 35214 KD", "Toyota Corolla", "Argent", "Chantal Nkumu", "+243 817 550 331", False),
    ("4567 KB", "Ford Ranger", "Blanc", "Societe Trans-Kongo SARL", "+243 810 900 471", False),
    ("8891 KC", "Camion FUSO Canter", "Vert", "Alphonse Kalonji", "+243 828 117 654", False),
    ("2310 KE", "Hyundai H1", "Noir", "Grace Mbuyi", "+243 892 305 218", False),
    ("7742 KD", "Peugeot 404 pickup", "Jaune", "Didier Tshibangu", "+243 813 662 047", False),
    ("6083 KB", "Toyota Land Cruiser", "Blanc", "ONG Santé Kongo", "+243 899 140 785", False),
    ("QA 4127 KD", "Nissan Patrol", "Noir", "Marceline Lokwa", "+243 816 478 920", False),
    ("RB 9034 KD", "Moto-taxi", "Rouge", "Espoir Mukendi", "+243 841 209 633", False),
    ("1195 KC", "Renault Kangoo", "Blanc", "Boulangerie Kin-Matonge", "+243 820 571 349", False),
    ("5520 KD", "Isuzu NPR", "Blanc", "Menuiserie Ngomba", "+243 858 036 214", False),
    ("CD 45871 KD", "Mercedes Sprinter", "Gris", "Aline Bofenda", "+243 834 687 150", True),
    ("9867 KE", "Toyota RAV4", "Bleu nuit", "Olivier Kasongo", "+243 879 512 068", False),
    ("3402 KB", "Mitsubishi L200", "Vert", "Coopérative Agricole Mfumu", "+243 806 943 275", False),
]

DIRECTIONS = ["nord", "sud", "est", "ouest"]

DEMO_INCIDENTS = [
    # (type, description, lat, lng, severite, statut, heures avant maintenant, duree_h si resolue)
    (
        "accident",
        "Collision legere entre un taxi-bus et une moto au rond-point Ngaba, blesses legers, circulation ralentie sur une voie.",
        -4.3390, 15.3155, 2, IncidentStatus.CONFIRMED, 3.0, None,
    ),
    (
        "congestion",
        "Embouteillage majeur sur le boulevard Lumumba suite a un controle de police double, remontee de file sur 1,5 km.",
        -4.3650, 15.3550, 3, IncidentStatus.REPORTED, 0.7, None,
    ),
    (
        "panne_feux",
        "Panne des feux tricolores au carrefour de la 7e rue Limete, agents de circulation deployes, signalisation retablie.",
        -4.3700, 15.3280, 2, IncidentStatus.RESOLVED, 5.0, 0.5,
    ),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_polygon(name: str, lat: float, lng: float) -> str:
    """Petit rectangle GeoJSON (~1,8 km cote) autour du centre de la zone."""
    d = 0.008
    ring = [
        [round(lng - d, 6), round(lat - d, 6)],
        [round(lng + d, 6), round(lat - d, 6)],
        [round(lng + d, 6), round(lat + d, 6)],
        [round(lng - d, 6), round(lat + d, 6)],
        [round(lng - d, 6), round(lat - d, 6)],
    ]
    feature = {
        "type": "Feature",
        "properties": {"commune": name, "demo": True},
        "geometry": {"type": "Polygon", "coordinates": [ring]},
    }
    return json.dumps(feature, ensure_ascii=False)


def diurnal_factor(hour_float: float) -> float:
    """Courbe de trafic journaliere : pics a 8 h et 18 h 30, creux nocturnes."""
    morning = math.exp(-((hour_float - 8.0) ** 2) / 6.0)
    evening = math.exp(-((hour_float - 18.5) ** 2) / 9.0)
    return min(1.0, 0.12 + 0.88 * max(morning, evening))


def congestion_from_ratio(ratio: float) -> float:
    """Ratio occupation/capacite -> niveau de congestion [0, 1]."""
    return round(max(0.0, min(1.0, (ratio - 0.30) / 0.65)), 3)


# ---------------------------------------------------------------------------
# Nettoyage (lignes de demo uniquement, jamais les users)
# ---------------------------------------------------------------------------


async def delete_demo_data(session) -> dict[str, int]:
    deleted: dict[str, int] = {}

    res = await session.execute(
        delete(PlateReading).where(
            or_(
                PlateReading.camera_id.in_(
                    select(Camera.id).where(Camera.rtsp_url.startswith(RTSP_PREFIX))
                ),
                PlateReading.vehicle_id.in_(
                    select(Vehicle.id).where(Vehicle.plate_number.in_(
                        [v[0] for v in VEHICLE_FLEET]))
                ),
            )
        )
    )
    deleted["plate_readings"] = res.rowcount

    res = await session.execute(
        delete(TrafficMetric).where(
            TrafficMetric.zone_id.in_(
                select(TrafficZone.id).where(TrafficZone.name.in_([z[0] for z in DEMO_ZONES]))
            )
        )
    )
    deleted["traffic_metrics"] = res.rowcount

    incident_conds = [
        (Incident.type == t) & (Incident.latitude == lat) & (Incident.longitude == lng)
        for t, _d, lat, lng, *_rest in DEMO_INCIDENTS
    ]
    res = await session.execute(delete(Incident).where(or_(*incident_conds)))
    deleted["incidents"] = res.rowcount

    res = await session.execute(delete(Camera).where(Camera.rtsp_url.startswith(RTSP_PREFIX)))
    deleted["cameras"] = res.rowcount

    res = await session.execute(
        delete(Vehicle).where(Vehicle.plate_number.in_([v[0] for v in VEHICLE_FLEET]))
    )
    deleted["vehicles"] = res.rowcount

    res = await session.execute(
        delete(TrafficZone).where(TrafficZone.name.in_([z[0] for z in DEMO_ZONES]))
    )
    deleted["traffic_zones"] = res.rowcount

    await session.commit()
    return deleted


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


async def get_admin_id(session) -> int | None:
    from app.models import User

    admin_id = await session.scalar(
        select(User.id).where(User.role == "ADMIN").limit(1)
    )
    return admin_id


async def seed(session) -> dict[str, int]:
    counts: dict[str, int] = {}
    now = utcnow()

    # --- Zones ------------------------------------------------------------
    zones_by_name: dict[str, TrafficZone] = {}
    for name, description, lat, lng, _capacity, _freeflow in DEMO_ZONES:
        zone = TrafficZone(
            name=name,
            description=f"[démo] {description}",
            polygon=make_polygon(name, lat, lng),
            congestion_level=0.0,
            vehicle_count=0,
            average_speed=0.0,
            updated_at=now,
        )
        session.add(zone)
        zones_by_name[name] = zone
    counts["traffic_zones"] = len(zones_by_name)

    # --- Cameras ----------------------------------------------------------
    cameras: list[Camera] = []
    for _zone_name, cam_name, location, lat, lng, status, is_360 in CAMERA_SPOTS:
        cameras.append(
            Camera(
                name=cam_name,
                location=location,
                latitude=lat,
                longitude=lng,
                rtsp_url=f"{RTSP_PREFIX}{cam_name.lower()}.stream",
                status=status,
                is_360=is_360,
                created_at=now - timedelta(days=random.randint(30, 400)),
                updated_at=now - timedelta(hours=random.randint(1, 48)),
            )
        )
    session.add_all(cameras)
    counts["cameras"] = len(cameras)

    # --- Vehicules --------------------------------------------------------
    vehicles: list[Vehicle] = []
    for plate, vtype, color, owner, phone, stolen in VEHICLE_FLEET:
        vehicles.append(
            Vehicle(
                plate_number=plate,
                vehicle_type=vtype,
                color=color,
                owner_name=owner,
                owner_phone=phone,
                is_stolen=stolen,
                created_at=now - timedelta(days=random.randint(10, 300)),
                updated_at=now,
            )
        )
    session.add_all(vehicles)
    counts["vehicles"] = len(vehicles)

    await session.flush()  # recupere les ids

    # --- Lectures de plaques (48 h) --------------------------------------
    online_cams = [c for c in cameras if c.status == CameraStatus.ONLINE]
    readings: list[PlateReading] = []
    for i in range(72):
        vehicle = random.choice(vehicles)
        camera = random.choice(online_cams)
        ts = now - timedelta(minutes=random.uniform(0, 48 * 60))
        hour_f = ts.hour + ts.minute / 60.0
        busy = diurnal_factor(hour_f)
        speed = max(6.0, 45.0 * (1.0 - 0.70 * busy) + random.uniform(-4.0, 4.0))
        readings.append(
            PlateReading(
                vehicle_id=vehicle.id,
                camera_id=camera.id,
                plate_number=vehicle.plate_number,
                confidence=round(random.uniform(0.85, 0.99), 3),
                image_url=f"https://images.demo.trafic-kinshasa.local/plates/{i:04d}_{vehicle.plate_number.replace(' ', '_')}.jpg",
                direction=random.choice(DIRECTIONS),
                speed=round(speed, 1),
                timestamp=ts,
            )
        )
    session.add_all(readings)
    counts["plate_readings"] = len(readings)

    # --- Metriques de trafic (24 h / 15 min / zone) -----------------------
    metrics: list[TrafficMetric] = []
    latest_snapshot: dict[int, dict] = {}
    steps = 96  # 24 h / 15 min
    for (name, _desc, _lat, _lng, capacity, freeflow), zone in zip(DEMO_ZONES, zones_by_name.values()):
        occupancy_target = random.uniform(0.60, 0.78)
        for step in range(steps):
            ts = now - timedelta(minutes=15 * (steps - 1 - step))
            hour_f = ts.hour + ts.minute / 60.0
            ratio = min(
                1.02,
                max(0.03, occupancy_target * diurnal_factor(hour_f) * random.uniform(0.78, 1.22)),
            )
            count = round(capacity * ratio)
            congestion = congestion_from_ratio(ratio)
            avg_speed = round(max(6.0, freeflow * (1.0 - 0.78 * congestion) + random.uniform(-3.0, 3.0)), 1)
            metrics.append(
                TrafficMetric(
                    zone_id=zone.id,
                    vehicle_count=count,
                    average_speed=avg_speed,
                    congestion_level=congestion,
                    timestamp=ts,
                )
            )
            latest_snapshot[zone.id] = {
                "vehicle_count": count,
                "average_speed": avg_speed,
                "congestion_level": congestion,
            }
    session.add_all(metrics)
    counts["traffic_metrics"] = len(metrics)

    # Snapshot temps reel sur chaque zone (dashboard)
    for zone in zones_by_name.values():
        snap = latest_snapshot[zone.id]
        zone.vehicle_count = snap["vehicle_count"]
        zone.average_speed = snap["average_speed"]
        zone.congestion_level = snap["congestion_level"]
        zone.updated_at = now

    # --- Incidents ---------------------------------------------------------
    admin_id = await get_admin_id(session)
    for inc_type, description, lat, lng, severity, status, hours_ago, duration_h in DEMO_INCIDENTS:
        created = now - timedelta(hours=hours_ago)
        resolved = created + timedelta(hours=duration_h) if duration_h is not None else None
        session.add(
            Incident(
                type=inc_type,
                description=f"[démo] {description}",
                latitude=lat,
                longitude=lng,
                severity=severity,
                status=status,
                reported_by=admin_id,
                created_at=created,
                resolved_at=resolved,
            )
        )
    counts["incidents"] = len(DEMO_INCIDENTS)

    await session.commit()
    return counts


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def table_totals(session) -> dict[str, int]:
    totals = {}
    for model in (TrafficZone, Camera, Vehicle, PlateReading, TrafficMetric, Incident):
        totals[model.__tablename__] = await session.scalar(select(func.count()).select_from(model))
    return totals


async def run(db_url: str, clear_only: bool) -> None:
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            deleted = await delete_demo_data(session)
            removed = sum(deleted.values())
            label = "--clear : lignes de démo supprimées" if clear_only else "anciennes lignes de démo remplacées"
            print(f"[nettoyage] {label} ({removed} ligne(s))")
            for table, n in deleted.items():
                if n:
                    print(f"  - {table}: {n}")

            if clear_only:
                print("Terminé (--clear). Utilisateurs non touchés.")
                return

            inserted = await seed(session)

            print("\n=== Données de démonstration insérées ===")
            for table, n in inserted.items():
                print(f"  + {table}: {n}")

            totals = await table_totals(session)
            print("\n=== Totaux par table ===")
            for table, total in totals.items():
                print(f"  {table}: {total}")
            print("\nUtilisateurs : intacts.")
    finally:
        await engine.dispose()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed de données de démo Urban Traffic (Kinshasa).")
    parser.add_argument("--db", default=DEFAULT_DB_URL, help="URL SQLAlchemy async (defaut: SQLite backend)")
    parser.add_argument("--clear", action="store_true", help="Supprimer uniquement les lignes de démo")
    args = parser.parse_args()

    for attempt in range(1, 4):
        try:
            await run(args.db, args.clear)
            return
        except OperationalError as exc:
            if "database is locked" not in str(exc).lower() or attempt == 3:
                raise
            print(f"SQLite verrouillée (serveur uvicorn en lecture ?), nouvel essai dans 2 s ({attempt}/3)...")
            await asyncio.sleep(2.0)


if __name__ == "__main__":
    asyncio.run(main())
