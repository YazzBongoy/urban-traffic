
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.camera import CameraCreate, CameraResponse
from app.services.auth import require_operator
from app.services.camera import CameraService
from app.services.ingest import get_or_create_vehicle, record_plate_reading
from app.services.vision import analyze_image, models_available

router = APIRouter()


@router.get("/", response_model=list[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)):
    camera_service = CameraService(db)
    return await camera_service.get_all()


@router.post("/", response_model=CameraResponse, status_code=201)
async def create_camera(
    camera: CameraCreate,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_operator),
):
    camera_service = CameraService(db)
    return await camera_service.create(camera)


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
):
    camera_service = CameraService(db)
    camera = await camera_service.get_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.get("/{camera_id}/status")
async def get_camera_status(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
):
    camera_service = CameraService(db)
    return await camera_service.get_status(camera_id)


@router.post("/{camera_id}/analyze")
async def analyze_camera_frame(
    camera_id: int,
    file: UploadFile = File(...),
    identify: bool = True,
    read_plates: bool = False,
    persist: bool = False,
    min_plate_confidence: float = 0.6,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_operator),
):
    """Analyse une image de la caméra : détection véhicules, marque/modèle, lecture des plaques.

    Avec persist=true, chaque plaque lue (>= min_plate_confidence) crée/récupère le véhicule
    et enregistre un passage (PlateReading) — Phase 2 RNI.
    """
    camera_service = CameraService(db)
    camera = await camera_service.get_by_id(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")

    if not models_available():
        raise HTTPException(
            status_code=503,
            detail="Modèles ML non disponibles (voir ml/models/)",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Image vide")

    try:
        result = analyze_image(
            image_bytes,
            identify=identify,
            read_plates=read_plates,
            min_plate_confidence=min_plate_confidence,
        )
    except (RuntimeError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Analyse impossible : {exc}") from exc

    persisted: list[dict] = []
    if persist and read_plates:
        for det in result["detections"]:
            plate = det.get("plate")
            if not plate or plate["confidence"] < min_plate_confidence:
                continue
            vehicle = await get_or_create_vehicle(
                db, plate["text"], vehicle_type=det["vehicle_type"]
            )
            reading = await record_plate_reading(
                db,
                camera_id=camera_id,
                plate_number=plate["text"],
                confidence=plate["confidence"],
                vehicle_id=vehicle.id,
            )
            persisted.append(
                {
                    "reading_id": reading.id,
                    "vehicle_id": vehicle.id,
                    "plate_number": plate["text"],
                    "plate_confidence": plate["confidence"],
                }
            )
        await db.commit()

    return {
        "camera_id": camera_id,
        "camera_name": camera.name,
        "filename": file.filename,
        "persisted_readings": persisted,
        **result,
    }
