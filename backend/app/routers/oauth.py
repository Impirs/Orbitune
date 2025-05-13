from fastapi import APIRouter
from app.services import oauth_google, oauth_spotify, oauth_yandex

router = APIRouter()

router.include_router(oauth_google.router)
router.include_router(oauth_spotify.router)
router.include_router(oauth_yandex.router)
