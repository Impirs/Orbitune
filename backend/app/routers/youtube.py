from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import ConnectedService
from app.services.platforms.youtube import YouTubeService
from typing import List

router = APIRouter(prefix="/youtube", tags=["youtube"])

@router.get("/playlists")
def get_youtube_playlists(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    service = db.query(ConnectedService).filter_by(user_id=user_id, platform="youtube").first()
    if not service:
        raise HTTPException(status_code=404, detail="YouTube not connected")
    playlists = YouTubeService(db, user_id).get_playlists()
    return {"playlists": playlists}

@router.post("/import_playlists")
def import_youtube_playlists(data: dict, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    playlist_ids: List[str] = data.get("playlist_ids")
    if not playlist_ids:
        raise HTTPException(status_code=400, detail="No playlists selected")
    service = db.query(ConnectedService).filter_by(user_id=user_id, platform="youtube").first()
    if not service:
        raise HTTPException(status_code=404, detail="YouTube not connected")
    yt_service = YouTubeService(db, user_id)
    all_playlists = {pl["id"]: pl for pl in yt_service.get_playlists()}
    for pid in playlist_ids:
        pl = all_playlists.get(pid)
        if not pl:
            continue
        # Импортируем только выбранные плейлисты и их треки
        tracks = yt_service.get_playlist_tracks(pid)
        from app.models.models import UserPlaylist, PlaylistTrack, Track, TrackAvailability
        session = db
        db_pl = session.query(UserPlaylist).filter_by(user_id=user_id, external_id=pl["id"], source_platform="youtube").first()
        if not db_pl:
            db_pl = UserPlaylist(
                user_id=user_id,
                title=pl["title"],
                description=pl.get("description"),
                source_platform="youtube",
                external_id=pl["id"],
                updated_at=None,
                image_url=pl.get("cover_url"),
                is_public=True,
                tracks_number=len(tracks)
            )
            session.add(db_pl)
            session.flush()
        else:
            db_pl.title = pl["title"]
            db_pl.description = pl.get("description")
            db_pl.updated_at = None
            db_pl.image_url = pl.get("cover_url")
            db_pl.tracks_number = len(tracks)
        session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
        seen_track_ids = set()
        for idx, t in enumerate(tracks):
            db_track = session.query(Track).filter_by(title=t["title"], artist=t["artist"]).first()
            if not db_track:
                db_track = Track(
                    title=t["title"],
                    artist=t["artist"],
                    album=t.get("album"),
                    duration=t.get("duration"),
                    image_url=t.get("cover_url")
                )
                session.add(db_track)
                session.flush()
            avail = session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="youtube").first()
            if not avail:
                avail = TrackAvailability(
                    track_id=db_track.id,
                    platform="youtube",
                    external_id=t["id"],
                    url=None,
                    available=True
                )
                session.add(avail)
            else:
                avail.external_id = t["id"]
                avail.available = True
                avail.last_checked_at = datetime.utcnow()
            if db_track.id not in seen_track_ids:
                session.add(PlaylistTrack(
                    playlist_id=db_pl.id,
                    platform="youtube",
                    track_id=db_track.id,
                    order_index=idx
                ))
                seen_track_ids.add(db_track.id)
        session.commit()
    return {"ok": True}
