from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserFavorite, Track, ConnectedService, UserPlaylist, PlaylistTrack
from app.services.platforms import SpotifyService
import logging

router = APIRouter()

@router.get("")
def favorites(user_id: int = None, db: Session = Depends(get_db)):
    if not user_id:
        return {"playlist": None, "tracks": [], "error": "user_id is required"}
    try:
        # Получаем плейлист Liked Songs из user_favorites
        fav = db.query(UserFavorite).filter_by(user_id=user_id, platform="spotify").first()
        if not fav:
            return {"playlist": None, "tracks": []}
        # Находим плейлист Liked Songs в user_playlists
        pl = db.query(UserPlaylist).filter((UserPlaylist.external_id == fav.playlist_id) | (UserPlaylist.id == fav.playlist_id)).first()
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
        return {
            "playlist": {
                "id": fav.playlist_id,
                "title": fav.title,
                "description": fav.description,
                "platform": fav.platform,
                "tracks_count": len(tracks)
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
