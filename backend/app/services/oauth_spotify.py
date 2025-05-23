import os
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from app.database import get_db
from app.routers.crud import add_connected_service
from sqlalchemy.orm import Session
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
import importlib

requests = importlib.import_module("requests")

router = APIRouter(prefix="/oauth/spotify", tags=["oauth-spotify"])

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

@router.get("/login")
def spotify_login(request: StarletteRequest):
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": "user-read-email user-library-read playlist-read-private streaming",
        "show_dialog": "true"
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/callback")
def spotify_callback(request: StarletteRequest, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=spotify&reason=no_code")
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=spotify&reason=token_error")
    tokens = resp.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if not access_token:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=spotify&reason=no_access_token")
    # Получаем инфо о пользователе
    userinfo = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"}).json()
    external_user_id = userinfo.get("id")
    if not external_user_id:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=spotify&reason=no_external_user_id")
    # Получаем user_id из сессии
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=spotify&reason=no_user_id")
    add_connected_service(db, user_id, "spotify", external_user_id, access_token, refresh_token)
    # Синхронизация плейлистов и треков пользователя
    try:
        from app.services.platforms.platforms import SpotifyService
        SpotifyService(db, user_id).sync_user_playlists_and_favorites()
    except Exception as e:
        import logging
        logging.error(f"[SPOTIFY SYNC] Ошибка при синхронизации: {e}")
    # Получаем nickname пользователя для редиректа
    from app.models.models import User
    user = db.query(User).filter_by(id=user_id).first()
    nickname = user.nickname if user else "home"
    return RedirectResponse(f"http://127.0.0.1:5173/{nickname}/home?oauth=success&platform=spotify")
