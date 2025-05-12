from fastapi import APIRouter
from app.services import oauth_google, oauth_spotify

router = APIRouter()

router.include_router(oauth_google.router)
router.include_router(oauth_spotify.router)
