from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserPlaylist, PlaylistTrack, Track, ConnectedService
from app.services.platforms import SpotifyService
import logging

router = APIRouter()

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
                "id": pl.external_id or pl.id,
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
                    "cover_url": t.cover_url,
                } for t in tracks
            ],
            "tracks_count": len(tracks)
        }
    except Exception as e:
        logging.error(f"Error getting playlist tracks: {str(e)}")
        return {"tracks": [], "tracks_count": 0, "error": str(e)}
