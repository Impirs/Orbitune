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
        raise HTTPException(status_code=400, detail="No code provided")
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
        raise HTTPException(status_code=400, detail="Failed to get token")
    tokens = resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    # Получаем инфо о пользователе
    userinfo = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": f"Bearer {access_token}"}).json()
    external_user_id = userinfo["id"]
    # Получаем user_id из сессии
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    add_connected_service(db, user_id, "spotify", external_user_id, access_token, refresh_token)
    return {"msg": "Spotify account connected"}
