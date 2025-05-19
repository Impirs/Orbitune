from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserFavorite, Track, ConnectedService, UserPlaylist, PlaylistTrack
from app.services.platforms.platforms import get_platform_service
import logging

router = APIRouter()

@router.get("")
def favorites(user_id: int = None, platform: str = "spotify", db: Session = Depends(get_db)):
    if not user_id:
        return {"playlist": None, "tracks": [], "error": "user_id is required"}
    try:
        # Получаем плейлист избранного для выбранной платформы
        fav = db.query(UserFavorite).filter_by(user_id=user_id, platform=platform).first()
        if not fav:
            return {"playlist": None, "tracks": []}
        # Находим плейлист избранного в user_playlists
        pl = db.query(UserPlaylist).filter(
            ((UserPlaylist.external_id == fav.playlist_id) | (UserPlaylist.id == fav.playlist_id)) &
            (UserPlaylist.source_platform == platform)
        ).first()
        if not pl:
            return {"playlist": None, "tracks": []}
        # Получаем треки из PlaylistTrack и Track
        tracks = (
            db.query(Track)
            .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
            .filter(PlaylistTrack.playlist_id == pl.id)
            .order_by(PlaylistTrack.order_index)
            .all()
        )
        # Получаем сервис платформы для дополнительной информации (например, cover_url)
        service = get_platform_service(platform, db, user_id)
        playlist_info = service.get_liked_playlist_info() if hasattr(service, 'get_liked_playlist_info') else {}
        return {
            "playlist": {
                "id": fav.playlist_id,
                "title": fav.title or playlist_info.get("title"),
                "description": fav.description or playlist_info.get("description"),
                "platform": fav.platform,
                "tracks_count": len(tracks),
                "cover_url": playlist_info.get("cover_url")
            },
            "tracks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "artist": t.artist,
                    "album": t.album,
                    "duration": t.duration,
                    "image_url": t.image_url
                } for t in tracks
            ]
        }
    except Exception as e:
        logging.error(f"Error getting favorites: {str(e)}")
        return {"playlist": None, "tracks": []}
