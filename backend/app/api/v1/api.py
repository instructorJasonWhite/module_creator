from fastapi import APIRouter

from .endpoints import agents, auth, documents, system, user_preferences

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(
    user_preferences.router, prefix="/preferences", tags=["preferences"]
)
