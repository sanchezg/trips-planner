from fastapi import APIRouter, Depends

from app.db.models.user import User
from app.dependencies.auth import get_current_user
from app.services.google_maps.service import autocomplete, geocode

router = APIRouter()


@router.get("/autocomplete")
async def maps_autocomplete(input: str, current_user: User = Depends(get_current_user)) -> dict:
    return await autocomplete(input)


@router.get("/geocode")
async def maps_geocode(address: str, current_user: User = Depends(get_current_user)) -> dict:
    return await geocode(address)
