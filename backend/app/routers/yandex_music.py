from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ConnectedService
# from app.libs.yandex_music_token import get_token  # Оставлено для истории, если Яндекс снова откроет ручную авторизацию
from pydantic import BaseModel
from app.services.platforms.yandex import YandexMusicService

router = APIRouter(prefix="/yandex_music", tags=["yandex-music"])

class YandexMusicAuthRequest(BaseModel):
    user_id: int
    login: str = None
    password: str = None
    xtoken: str = None

@router.post("/xtoken")
def get_and_save_xtoken(data: YandexMusicAuthRequest, db: Session = Depends(get_db)):
    try:
        # --- Новый путь: пользователь вручную вставляет xtoken ---
        if data.xtoken:
            xtoken = data.xtoken
        # --- Старый путь: попытка получить xtoken через логин/пароль (оставлено для истории, не работает) ---
        # elif data.login and data.password:
        #     xtoken = get_token(data.login, data.password)
        else:
            raise HTTPException(status_code=400, detail="Необходимо передать xtoken (ручной способ)")
        # Сохраняем xtoken в ConnectedService с platform='yandex-music'
        service = db.query(ConnectedService).filter_by(user_id=data.user_id, platform='yandex-music').first()
        if not service:
            service = ConnectedService(
                user_id=data.user_id,
                platform='yandex-music',
                external_user_id=data.login or "manual",
                access_token=xtoken
            )
            db.add(service)
        else:
            service.access_token = xtoken
        db.commit()
        # --- Автоматическая синхронизация после добавления xtoken ---
        try:
            YandexMusicService(db, data.user_id).sync_user_playlists_and_favorites()
        except Exception as sync_err:
            import logging
            logging.error(f"[YANDEX SYNC] Ошибка при автосинхронизации: {sync_err}")
        return {"ok": True, "xtoken": xtoken}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка получения xtoken: {e}")
