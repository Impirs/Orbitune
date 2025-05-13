from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import UserFavorite, Track

router = APIRouter()

@router.get("/")
def favorites(user_id: int, db: Session = Depends(get_db)):
    favs = db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
    result = []
    for fav in favs:
        track = db.query(Track).filter(Track.id == fav.track_id).first()
        if track:
            result.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "album": track.album,
                "duration": track.duration,
                "cover_url": track.cover_url,
                "platform": fav.platform,
            })
    return result
