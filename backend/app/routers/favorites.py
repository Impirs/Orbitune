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
        return {"playlist": None, "error": "user_id is required"}
    try:
        fav = db.query(UserFavorite).filter_by(user_id=user_id, platform=platform).first()
        if not fav:
            return {"playlist": None}
        return {
            "playlist": {
                "external_id": fav.external_id,
                "title": fav.title,
                "platform": fav.platform,
                "tracks_number": fav.tracks_number
            }
        }
    except Exception as e:
        logging.error(f"Error getting favorites: {str(e)}")
        return {"playlist": None, "error": str(e)}
