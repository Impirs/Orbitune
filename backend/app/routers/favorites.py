from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserFavorite, Track, ConnectedService
from app.services.platforms import SpotifyService
import logging

router = APIRouter()

@router.get("")
def favorites(user_id: int = None, db: Session = Depends(get_db)):
    if not user_id:
        return {"playlist": None, "tracks": [], "error": "user_id is required"}
    try:
        # Проверяем, есть ли подключённый Spotify
        spotify_service = db.query(ConnectedService).filter_by(user_id=user_id, platform="spotify").first()
        if spotify_service:
            # Получаем плейлист Liked Songs из user_favorites
            fav = db.query(UserFavorite).filter_by(user_id=user_id, platform="spotify").first()
            spotify = SpotifyService(db, user_id)
            tracks = []
            if fav and fav.playlist_id:
                # Получаем все треки из Liked Songs по ключу (playlist_id)
                # Для Spotify Liked Songs используем get_favorite_tracks_all
                tracks = spotify.get_favorite_tracks_all()
            return {
                "playlist": {
                    "id": fav.playlist_id if fav else None,
                    "title": fav.title if fav else "Liked Songs",
                    "description": fav.description if fav else "",
                    "platform": "spotify",
                    "tracks_count": len(tracks)
                },
                "tracks": tracks
            }
        # ...если нет Spotify — можно добавить обработку для других платформ...
        return {"playlist": None, "tracks": []}
    except Exception as e:
        logging.error(f"Error getting favorites: {str(e)}")
        return {"playlist": None, "tracks": []}
