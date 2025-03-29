from fastapi import APIRouter

from .endpoints import auth, system

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
