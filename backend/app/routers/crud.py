from sqlalchemy.orm import Session
from app.models.models import User, ConnectedService, UserPlaylist, Track
from sqlalchemy.exc import IntegrityError

def create_user(db: Session, email: str, password_hash: str, nickname: str, is_admin: bool = False):
    db_user = User(email=email, password_hash=password_hash, nickname=nickname, is_admin=is_admin)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_nickname(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()

def create_playlist(db: Session, user_id: int, title: str, description: str = None, source_platform: str = None, is_mixed: bool = False):
    playlist = UserPlaylist(user_id=user_id, title=title, description=description, source_platform=source_platform, is_mixed=is_mixed)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist

def add_connected_service(db: Session, user_id: int, platform: str, external_user_id: str, access_token: str, refresh_token: str = None, expires_at = None):
    service = ConnectedService(user_id=user_id, platform=platform, external_user_id=external_user_id, access_token=access_token, refresh_token=refresh_token, expires_at=expires_at)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

def get_connected_services(db: Session, user_id: int):
    return db.query(ConnectedService).filter(ConnectedService.user_id == user_id).all()