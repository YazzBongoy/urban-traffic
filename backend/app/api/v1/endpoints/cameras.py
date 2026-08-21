
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.camera import CameraCreate, CameraResponse
from app.services.auth import require_operator
from app.services.camera import CameraService
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
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_operator),
):
    """Analyse une image de la caméra : détection véhicules + marque/modèle (Phase 2)."""
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
        result = analyze_image(image_bytes, identify=identify)
    except (RuntimeError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"Analyse impossible : {exc}") from exc

    return {
        "camera_id": camera_id,
        "camera_name": camera.name,
        "filename": file.filename,
        **result,
    }
