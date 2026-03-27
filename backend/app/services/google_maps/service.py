import httpx
from app.core.config import settings


async def autocomplete(input_text: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/place/autocomplete/json",
            params={"input": input_text, "key": settings.google_maps_api_key},
        )
        response.raise_for_status()
        return response.json()


async def geocode(address: str) -> dict:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": settings.google_maps_api_key},
        )
        response.raise_for_status()
        return response.json()
