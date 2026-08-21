import asyncio

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import engine

app = FastAPI(
    title="Urban Traffic Management API",
    description="API for urban traffic management using 360° cameras and license plate recognition",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(response: Response):
    checks = {"database": False, "redis": False}

    try:
        async with asyncio.timeout(2):
            async with engine.connect() as conn:
                await conn.exec_driver_sql("SELECT 1")
        checks["database"] = True
    except Exception:
        pass

    try:
        import redis.asyncio as aioredis_client

        async with asyncio.timeout(2):
            client = aioredis_client.from_url(settings.REDIS_URL, socket_connect_timeout=2)
            await client.ping()
            await client.aclose()
        checks["redis"] = True
    except Exception:
        pass

    if not all(checks.values()):
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ready" if all(checks.values()) else "degraded", "checks": checks}
