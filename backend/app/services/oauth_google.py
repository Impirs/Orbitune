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

router = APIRouter(prefix="/oauth/google", tags=["oauth-google"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@router.get("/login")
def google_login(request: StarletteRequest):
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/youtube.readonly",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/callback")
def google_callback(request: StarletteRequest, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=google&reason=no_code")
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=google&reason=token_error")
    tokens = resp.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    if not access_token:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=google&reason=no_access_token")
    userinfo = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers={"Authorization": f"Bearer {access_token}"}).json()
    external_user_id = userinfo.get("id")
    if not external_user_id:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=google&reason=no_external_user_id")
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=google&reason=no_user_id")
    add_connected_service(db, user_id, "google", external_user_id, access_token, refresh_token)
    from app.models.models import User
    user = db.query(User).filter_by(id=user_id).first()
    nickname = user.nickname if user else "home"
    return RedirectResponse(f"http://127.0.0.1:5173/{nickname}/home?oauth=success&platform=google")
