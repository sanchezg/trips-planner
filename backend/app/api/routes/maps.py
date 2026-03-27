from fastapi import APIRouter
from app.services.google_maps.service import autocomplete, geocode

router = APIRouter()


@router.get("/autocomplete")
async def maps_autocomplete(input: str) -> dict:
    return await autocomplete(input)


@router.get("/geocode")
async def maps_geocode(address: str) -> dict:
    return await geocode(address)
