from fastapi import APIRouter
from app.services import oauth_google, oauth_spotify, oauth_yandex
from app.routers.youtube_import import router as youtube_import_router

router = APIRouter()

router.include_router(oauth_google.router)
router.include_router(oauth_spotify.router)
router.include_router(oauth_yandex.router)
router.include_router(youtube_import_router)
