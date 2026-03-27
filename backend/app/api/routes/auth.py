from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_session_token
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.user_repository import get_or_create_google_user
from app.schemas.user import UserRead
from app.services.auth.google_oauth import build_google_login_url, exchange_code_for_user

router = APIRouter()


@router.get("/google/login")
async def google_login() -> RedirectResponse:
    return RedirectResponse(build_google_login_url())


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    payload = await exchange_code_for_user(code)
    user = get_or_create_google_user(
        db,
        email=payload["email"],
        name=payload.get("name"),
        avatar_url=payload.get("picture"),
        google_sub=payload["sub"],
    )
    token = create_session_token({"user_id": user.id, "email": user.email})
    response = RedirectResponse(settings.app_url + "/dashboard")
    response.set_cookie("trip_session", token, httponly=True, secure=False, samesite="lax")
    return response


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout() -> Response:
    response = Response(status_code=204)
    response.delete_cookie("trip_session")
    return response
