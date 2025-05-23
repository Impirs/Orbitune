from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.platforms.youtube import YouTubeService

router = APIRouter(prefix="/youtube", tags=["youtube"])

@router.get("/fetch_temp_data")
def fetch_temp_data(user_id: int, db: Session = Depends(get_db)):
    service = YouTubeService(db, user_id)
    return {"playlists": service.fetch_service_temp_data()}

@router.post("/import_playlists")
async def import_playlists(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user_id = data.get("user_id")
    playlists = data.get("playlists")
    if not user_id or not playlists:
        raise HTTPException(400, "Missing data")
    service = YouTubeService(db, user_id)
    service.save_selected_playlists(playlists)
    return {"ok": True}
