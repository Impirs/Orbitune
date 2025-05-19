from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.crud import get_connected_services
from app.models.models import ConnectedService, UserPlaylist, PlaylistTrack, UserFavorite
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
                service = None
                try:
                    from app.services.platforms.platforms import get_platform_service
                    service = get_platform_service(s.platform, db, user_id)
                except Exception as e:
                    logging.error(f"Error creating platform service for {s.platform}: {e}")
                if service and hasattr(service, 'get_stats'):
                    stats = service.get_stats()
                    info["display_name"] = stats.get("display_name")
                    info["subscription_type"] = stats.get("subscription_type", "—")
                    if "songs" in stats:
                        info["songs"] = stats.get("songs", 0)
                    if "playlists" in stats:
                        info["playlists"] = stats.get("playlists", 0)
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
        # 1. Найти все user_playlists по юзеру и сервису
        playlists = db.query(UserPlaylist).filter_by(user_id=user_id, source_platform=platform).all()
        playlist_ids = [pl.id for pl in playlists]
        # 2. Удалить все playlist_tracks для этих плейлистов
        if playlist_ids:
            db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id.in_(playlist_ids)).delete(synchronize_session=False)
        # 3. Удалить сами user_playlists
        db.query(UserPlaylist).filter_by(user_id=user_id, source_platform=platform).delete(synchronize_session=False)
        # 4. Удалить user_favorites по юзеру и сервису
        db.query(UserFavorite).filter_by(user_id=user_id, platform=platform).delete(synchronize_session=False)
        # 5. Удалить саму привязку в connected_services
        db.query(ConnectedService).filter_by(user_id=user_id, platform=platform).delete(synchronize_session=False)
        db.commit()
        return {"ok": True}
    except Exception as e:
        logging.error(f"Error disconnecting service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error disconnecting service: {str(e)}")

@router.post("/sync")
def sync_platform(user_id: int, platform: str, db: Session = Depends(get_db)):
    import logging
    logging.info(f"[SYNC-ROUTER] Вызван sync для user_id={user_id}, platform={platform}")
    try:
        from app.services.platforms.platforms import get_platform_service
        service = get_platform_service(platform, db, user_id)
        service.sync_user_playlists_and_favorites()
        logging.info(f"[SYNC-ROUTER] sync_user_playlists_and_favorites вызван для user_id={user_id}, platform={platform}")
        return {"ok": True}
    except Exception as e:
        logging.error(f"Error syncing {platform}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error syncing {platform}: {str(e)}")
