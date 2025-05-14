from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.crud import get_connected_services
from app.models.models import ConnectedService
from app.services.platforms import SpotifyService
import logging

router = APIRouter(prefix="/connected_services", tags=["connected-services"])

@router.get("")
def list_connected_services(user_id: int, db: Session = Depends(get_db)):
    try:
        services = get_connected_services(db, user_id)
        result = []
        for s in services:
            info = {
                "id": s.id,
                "platform": s.platform,
                "external_user_id": s.external_user_id,
                "is_connected": True,
                "expires_at": s.expires_at,
            }
            try:
                if s.platform == "spotify":
                    spotify = SpotifyService(db, user_id)
                    stats = spotify.get_stats()
                    # Всегда добавлять ключевые поля
                    info["display_name"] = stats.get("display_name")
                    info["songs"] = stats.get("songs", 0)
                    info["playlists"] = stats.get("playlists", 0)
                    info["subscription_type"] = stats.get("subscription_type", "—")
            except Exception as e:
                logging.error(f"Error getting {s.platform} stats: {str(e)}")
                info["error"] = f"Could not retrieve service information: {str(e)}"
            result.append(info)
        return result
    except Exception as e:
        logging.error(f"Error listing connected services: {str(e)}")
        return []

@router.delete("")
def disconnect_service(user_id: int, platform: str, db: Session = Depends(get_db)):
    try:
        service = db.query(ConnectedService).filter_by(user_id=user_id, platform=platform).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        db.delete(service)
        db.commit()
        return {"ok": True}
    except Exception as e:
        logging.error(f"Error disconnecting service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error disconnecting service: {str(e)}")

@router.post("/sync")
def sync_spotify(user_id: int, db: Session = Depends(get_db)):
    import logging
    logging.info(f"[SYNC-ROUTER] Вызван sync для user_id={user_id}")
    try:
        spotify_service = db.query(ConnectedService).filter_by(user_id=user_id, platform="spotify").first()
        if not spotify_service:
            logging.warning(f"[SYNC-ROUTER] Нет подключенного Spotify для user_id={user_id}")
            raise HTTPException(status_code=404, detail="Spotify not connected")
        spotify = SpotifyService(db, user_id)
        spotify.sync_user_playlists_and_favorites()
        logging.info(f"[SYNC-ROUTER] sync_user_playlists_and_favorites вызван для user_id={user_id}")
        return {"ok": True}
    except Exception as e:
        logging.error(f"Error syncing Spotify: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error syncing Spotify: {str(e)}")
