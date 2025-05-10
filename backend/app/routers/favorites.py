from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.platforms import get_favorite_tracks

router = APIRouter()

@router.get("/")
def favorites(db: Session = Depends(get_db)):
    return get_favorite_tracks()
