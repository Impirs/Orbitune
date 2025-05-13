from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserPlaylist, PlaylistTrack, Track

router = APIRouter()

@router.get("/")
def get_playlists(user_id: int, db: Session = Depends(get_db)):
    # Получаем все плейлисты пользователя
    playlists = db.query(UserPlaylist).filter(UserPlaylist.user_id == user_id).all()
    result = []
    for pl in playlists:
        # Получаем треки для каждого плейлиста
        tracks = (
            db.query(Track)
            .join(PlaylistTrack, PlaylistTrack.track_id == Track.id)
            .filter(PlaylistTrack.playlist_id == pl.id)
            .all()
        )
        result.append({
            "id": pl.id,
            "title": pl.title,
            "description": pl.description,
            "source_platform": pl.source_platform,
            "is_mixed": pl.is_mixed,
            "tracks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "artist": t.artist,
                    "album": t.album,
                    "duration": t.duration,
                    "cover_url": t.cover_url,
                } for t in tracks
            ]
        })
    return result
