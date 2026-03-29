from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_oauth_state, create_session_token, read_oauth_state
from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.repositories.session_repository import create_user_session, revoke_session
from app.repositories.user_repository import get_or_create_google_user
from app.schemas.user import UserRead
from app.services.auth.google_oauth import build_google_login_url, exchange_code_for_user

router = APIRouter()


def _sanitize_next_path(next_path: str | None) -> str | None:
    if not next_path:
        return None
    if not next_path.startswith("/") or next_path.startswith("//"):
        return None
    return next_path


def _build_login_redirect_with_error(error_code: str) -> RedirectResponse:
    query = urlencode({"error": error_code})
    response = RedirectResponse(f"{settings.frontend_origin}/login?{query}")
    response.delete_cookie(
        settings.oauth_state_cookie_name,
        domain=settings.session_cookie_domain,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )
    return response


@router.get("/google/login")
async def google_login(next: str | None = None) -> RedirectResponse:
    safe_next = _sanitize_next_path(next)
    state, cookie_value = create_oauth_state(safe_next)
    response = RedirectResponse(build_google_login_url(state))
    response.set_cookie(
        settings.oauth_state_cookie_name,
        cookie_value,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=settings.oauth_state_max_age_seconds,
        domain=settings.session_cookie_domain,
    )
    return response


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str | None = None,
    oauth_state_cookie: str | None = Cookie(default=None, alias=settings.oauth_state_cookie_name),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    oauth_state = read_oauth_state(oauth_state_cookie, state)
    if not oauth_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OAuth state")

    payload = await exchange_code_for_user(code)
    email = payload["email"]
    if not settings.is_email_allowed_to_sign_in(email):
        return _build_login_redirect_with_error("unauthorized_email")

    user = get_or_create_google_user(
        db,
        email=email,
        name=payload.get("name"),
        avatar_url=payload.get("picture"),
        google_sub=payload["sub"],
        google_access_token=payload.get("access_token"),
        google_refresh_token=payload.get("refresh_token"),
        google_token_expires_at=payload.get("token_expires_at"),
    )
    token = create_session_token()
    create_user_session(db, user=user, session_token=token)
    redirect_path = _sanitize_next_path(oauth_state.get("next_path")) or "/dashboard"
    response = RedirectResponse(settings.frontend_origin + redirect_path)
    response.set_cookie(
        settings.session_cookie_name,
        token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.session_max_age_seconds,
        domain=settings.session_cookie_domain,
    )
    response.delete_cookie(
        settings.oauth_state_cookie_name,
        domain=settings.session_cookie_domain,
        secure=settings.session_cookie_secure,
        samesite="lax",
    )
    return response


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(
    trip_session: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    db: Session = Depends(get_db),
) -> Response:
    if trip_session:
        revoke_session(db, trip_session)

    response = Response(status_code=204)
    response.delete_cookie(
        settings.session_cookie_name,
        domain=settings.session_cookie_domain,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
    )
    return response
