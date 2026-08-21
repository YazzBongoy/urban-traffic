
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Camera
from app.schemas.camera import CameraCreate


class CameraService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> Sequence[Camera]:
        result = await self.db.execute(select(Camera))
        return result.scalars().all()

    async def get_by_id(self, camera_id: int) -> Camera | None:
        result = await self.db.execute(
            select(Camera).where(Camera.id == camera_id)
        )
        return result.scalar_one_or_none()

    async def create(self, camera_data: CameraCreate) -> Camera:
        camera = Camera(**camera_data.model_dump())
        self.db.add(camera)
        await self.db.commit()
        await self.db.refresh(camera)
        return camera

    async def get_status(self, camera_id: int) -> dict:
        camera = await self.get_by_id(camera_id)
        if not camera:
            return {"status": "not_found"}
        return {
            "id": camera.id,
            "name": camera.name,
            "status": camera.status,
            "is_360": camera.is_360,
        }
