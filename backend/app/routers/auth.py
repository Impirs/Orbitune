from fastapi import APIRouter, Depends, HTTPException, Request, Response, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.crud import create_user, get_user_by_email, get_user_by_nickname
from passlib.hash import bcrypt
import random
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel
import logging
import json
from app.models.models import ConnectedService

router = APIRouter()

NICKNAMES = ["Mercury", "Venus", "Earth", "Mars", "Saturn", "Uranus", "Neptune"]
ADMIN_EMAIL = "mtvaa8@gmail.com"  # Замените на ваш email для админа

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(data: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    logging.info(f"[REGISTER] Received: {data}")
    email = data.email
    password = data.password
    if not email or not password:
        logging.warning("[REGISTER] Email and password required")
        raise HTTPException(status_code=400, detail="Email and password required")
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        logging.warning(f"[REGISTER] Invalid email: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    if get_user_by_email(db, email):
        logging.warning(f"[REGISTER] User already exists: {email}")
        raise HTTPException(status_code=409, detail="User already exists")
    # Генерируем никнейм
    if email == ADMIN_EMAIL:
        nickname = "Jupiter"
        is_admin = True
    else:
        tries = 0
        while True:
            nickname = random.choice(NICKNAMES)
            if not get_user_by_nickname(db, nickname):
                break
            tries += 1
            if tries > 10:
                nickname = f"{random.choice(NICKNAMES)}{random.randint(1000,9999)}"
                break
        is_admin = False
    password_hash = bcrypt.hash(password)
    user = create_user(db, email, password_hash, nickname, is_admin)
    if not user:
        logging.error(f"[REGISTER] Nickname or email already exists: {email}, {nickname}")
        raise HTTPException(status_code=409, detail="Nickname or email already exists")
    
    # Set user in session
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["user_nickname"] = user.nickname
    
    logging.info(f"[REGISTER] User created: {user.email}, {user.nickname}, admin={user.is_admin}")
    return {"user": {"id": user.id, "email": user.email, "nickname": user.nickname, "is_admin": user.is_admin}}

@router.post("/login")
async def login(data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        logging.info(f"[LOGIN] Received: {data}")
        email = data.email
        password = data.password
        user = get_user_by_email(db, email)
        if not user:
            logging.warning(f"[LOGIN] User not found: {email}")
            raise HTTPException(status_code=404, detail="User not found")
        logging.info(f"[LOGIN] DB user: id={user.id}, email={user.email}, hash={user.password_hash}")
        if not bcrypt.verify(password, user.password_hash):
            logging.warning(f"[LOGIN] Invalid password for: {email}")
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Set user in session
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        request.session["user_nickname"] = user.nickname
        # --- Асинхронная синхронизация платформ ---
        for plat in ("spotify", "yandex"):
            plat_service = db.query(ConnectedService).filter_by(user_id=user.id, platform=plat).first()
            if plat_service and background_tasks is not None:
                def make_sync_bg(platform):
                    def sync_bg():
                        from app.services.platforms.platforms import get_platform_service
                        try:
                            logging.info(f"[LOGIN][BG] Start {platform} sync for user_id={user.id}")
                            service = get_platform_service(platform, db, user.id)
                            service.sync_user_playlists_and_favorites()
                            logging.info(f"[LOGIN][BG] {platform} sync finished for user_id={user.id}")
                        except Exception as e:
                            logging.error(f"[LOGIN][BG] {platform} sync error: {e}")
                    return sync_bg
                background_tasks.add_task(make_sync_bg(plat))
        logging.info(f"[LOGIN] Success: {user.email}, {user.nickname}, admin={user.is_admin}")
        return {"user": {"id": user.id, "email": user.email, "nickname": user.nickname, "is_admin": user.is_admin}}
    except Exception as e:
        logging.error(f"[LOGIN] Internal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.post("/logout")
async def logout(request: Request, response: Response):
    try:
        # Clear user from session
        request.session.pop("user_id", None)
        request.session.pop("user_email", None)
        request.session.pop("user_nickname", None)
        return {"success": True}
    except Exception as e:
        logging.error(f"[LOGOUT] Internal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/session")
async def get_session(request: Request):
    """Debug endpoint to check session state"""
    try:
        user_id = request.session.get("user_id")
        user_email = request.session.get("user_email")
        user_nickname = request.session.get("user_nickname")
        
        return {
            "user_id": user_id,
            "user_email": user_email,
            "user_nickname": user_nickname,
            "is_authenticated": user_id is not None
        }
    except Exception as e:
        logging.error(f"[SESSION] Internal error: {e}", exc_info=True)
        return {"error": str(e)}
