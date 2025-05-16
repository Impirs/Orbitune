from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserPlaylist, PlaylistTrack, Track, ConnectedService
from app.services.platforms import SpotifyService
import logging
from typing import List, Dict, Any

router = APIRouter()

@router.post("/sync_spotify")
def sync_spotify(user_id: int, db: Session = Depends(get_db)):
    """Явно вызываемый endpoint для синхронизации Spotify"""
    try:
        from app.services.platforms import SpotifyService
        spotify = SpotifyService(db, user_id)
        spotify.sync_user_playlists_and_favorites()
        return {"success": True}
    except Exception as e:
        logging.error(f"[SYNC_SPOTIFY] Internal error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@router.get("")
def get_playlists(user_id: int = None, db: Session = Depends(get_db)):
    if not user_id:
        return {"error": "user_id is required"}
    try:
        # Получаем все плейлисты пользователя из базы (быстро)
        playlists = db.query(UserPlaylist).filter(UserPlaylist.user_id == user_id).all()
        result = []
        for pl in playlists:
            result.append({
                "id": pl.id,  # внутренний id для фронта
                "external_id": pl.external_id,  # внешний id для синхронизации
                "title": pl.title,
                "description": pl.description,
                "source_platform": pl.source_platform,
                "is_mixed": pl.is_mixed,
                # Не возвращаем tracks и tracks_count сразу
            })
        return {"playlists": result}
    except Exception as e:
        logging.error(f"Error getting playlists: {str(e)}")
        return {"playlists": [], "error": str(e)}

@router.get("/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str, db: Session = Depends(get_db)):
    try:
        # Сначала ищем по external_id, если не найдено — по id
        pl = db.query(UserPlaylist).filter((UserPlaylist.external_id == playlist_id) | (UserPlaylist.id == playlist_id)).first()
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

@router.post("/tracks_count_batch")
def get_tracks_count_batch(ids: List[str] = Body(..., embed=True), db: Session = Depends(get_db)):
    try:
        logging.info(f"[tracks_count_batch] Получены ids: {ids}")
        int_ids = []
        str_ids = []
        for i in ids:
            try:
                int_ids.append(int(i))
            except Exception:
                str_ids.append(str(i))
        logging.info(f"[tracks_count_batch] int_ids: {int_ids}, str_ids: {str_ids}")
        playlists = db.query(UserPlaylist).filter(
            (UserPlaylist.external_id.in_(str_ids)) | (UserPlaylist.id.in_(int_ids))
        ).all()
        logging.info(f"[tracks_count_batch] Найдено плейлистов: {len(playlists)} ids: {[pl.id for pl in playlists]}, external_ids: {[pl.external_id for pl in playlists]}")
        id_map = {str(pl.external_id) if pl.external_id else str(pl.id): pl.id for pl in playlists}
        logging.info(f"[tracks_count_batch] id_map: {id_map}")
        counts = {}
        for req_id in ids:
            pl_id = id_map.get(str(req_id))
            if not pl_id:
                counts[req_id] = 0
                continue
            count = db.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == pl_id).count()
            counts[req_id] = count
        logging.info(f"[tracks_count_batch] counts: {counts}")
        return {"counts": counts}
    except Exception as e:
        logging.error(f"Error in tracks_count_batch: {str(e)}")
        return {"counts": {}, "error": str(e)}
