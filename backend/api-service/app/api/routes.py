from fastapi import APIRouter

from app.api.endpoints import posture
from app.core.config import settings

# Create the main router
router = APIRouter(prefix=settings.API_PREFIX)

# Include individual endpoint routers
router.include_router(posture.router, prefix="/posture", tags=["Posture Analysis"])
