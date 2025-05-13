import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from app.database import get_db
from app.routers.crud import add_connected_service
from sqlalchemy.orm import Session
from starlette.requests import Request as StarletteRequest
import importlib

requests = importlib.import_module("requests")

router = APIRouter(prefix="/oauth/yandex", tags=["oauth-yandex"])

YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")
YANDEX_REDIRECT_URI = os.getenv("YANDEX_REDIRECT_URI")

@router.get("/login")
def yandex_login(request: StarletteRequest):
    params = {
        "response_type": "code",
        "client_id": YANDEX_CLIENT_ID,
        "redirect_uri": YANDEX_REDIRECT_URI,
        "force_confirm": "yes",
        "scope": "login:email login:info music:read"
    }
    url = f"https://oauth.yandex.ru/authorize?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/callback")
def yandex_callback(request: StarletteRequest, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=yandex&reason=no_code")
    token_url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": YANDEX_CLIENT_ID,
        "client_secret": YANDEX_CLIENT_SECRET,
    }
    resp = requests.post(token_url, data=data)
    if resp.status_code != 200:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=yandex&reason=token_error")
    tokens = resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=yandex&reason=no_access_token")
    userinfo = requests.get("https://login.yandex.ru/info", headers={"Authorization": f"OAuth {access_token}"}).json()
    external_user_id = userinfo.get("id")
    if not external_user_id:
        return RedirectResponse(f"http://127.0.0.1:5173/auth?oauth=fail&platform=yandex&reason=no_external_user_id")
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("http://127.0.0.1:5173/auth?oauth=fail&platform=yandex&reason=no_user_id")
    add_connected_service(db, user_id, "yandex", external_user_id, access_token)
    from app.models.models import User
    user = db.query(User).filter_by(id=user_id).first()
    nickname = user.nickname if user else "home"
    return RedirectResponse(f"http://127.0.0.1:5173/{nickname}/home?oauth=success&platform=yandex")
