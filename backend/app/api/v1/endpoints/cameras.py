
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.camera import CameraCreate, CameraResponse
from app.services.auth import require_operator
from app.services.camera import CameraService

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
