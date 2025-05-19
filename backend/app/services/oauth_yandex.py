import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/oauth/yandex", tags=["oauth-yandex"])

@router.get("/login")
def yandex_login():
    return JSONResponse({
        "error": "OAuth авторизация Яндекс.Музыки не поддерживается. Используйте ручную авторизацию через /yandex_music/xtoken."
    }, status_code=400)

@router.get("/callback")
def yandex_callback():
    return JSONResponse({
        "error": "OAuth авторизация Яндекс.Музыки не поддерживается. Используйте ручную авторизацию через /yandex_music/xtoken."
    }, status_code=400)
