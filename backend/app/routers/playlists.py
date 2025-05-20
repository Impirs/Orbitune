from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserPlaylist, PlaylistTrack, Track, ConnectedService
from app.services.platforms.platforms import get_platform_service, PLATFORM_SERVICES
import logging
from typing import List, Dict, Any

router = APIRouter()

@router.post("/sync_platform")
def sync_platform(user_id: int, platform: str, db: Session = Depends(get_db)):
    """Явно вызываемый endpoint для синхронизации любой платформы"""
    try:
        service = get_platform_service(platform, db, user_id)
        service.sync_user_playlists_and_favorites()
        return {"success": True}
    except Exception as e:
        logging.error(f"[SYNC_PLATFORM] Internal error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@router.get("")
def get_playlists(user_id: int = None, platform: str = None, db: Session = Depends(get_db)):
    if not user_id:
        return {"error": "user_id is required"}
    try:
        query = db.query(UserPlaylist).filter(UserPlaylist.user_id == user_id)
        if platform:
            query = query.filter(UserPlaylist.source_platform == platform)
        playlists = query.all()
        result = []
        for pl in playlists:
            result.append({
                "id": pl.id,  # внутренний id для фронта
                "external_id": pl.external_id,  # внешний id для синхронизации
                "title": pl.title,
                "description": pl.description,
                "source_platform": pl.source_platform,
                "is_mixed": pl.is_mixed,
                "tracks_number": pl.tracks_number,
                "image_url": pl.image_url
            })
        return {"playlists": result}
    except Exception as e:
        logging.error(f"Error getting playlists: {str(e)}")
        return {"playlists": [], "error": str(e)}

@router.get("/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str, platform: str = None, db: Session = Depends(get_db)):
    try:
        # Сначала ищем по external_id, если не найдено — по id, с учётом платформы
        query = db.query(UserPlaylist).filter((UserPlaylist.external_id == playlist_id) | (UserPlaylist.id == playlist_id))
        if platform:
            query = query.filter(UserPlaylist.source_platform == platform)
        pl = query.first()
        if not pl:
            return {"tracks": [], "tracks_count": 0}
        tracks = (
            db.query(Track)
            .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
            .filter(PlaylistTrack.playlist_id == pl.id)
            .order_by(PlaylistTrack.order_index)
            .all()
        )
        return {
            "tracks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "artist": t.artist,
                    "album": t.album,
                    "duration": t.duration,
                    "image_url": t.image_url
                } for t in tracks
            ],
            "tracks_count": len(tracks)
        }
    except Exception as e:
        logging.error(f"Error getting playlist tracks: {str(e)}")
        return {"tracks": [], "tracks_count": 0, "error": str(e)}
