from .spotify import SpotifyService
from .yandex import YandexMusicService
from .youtube import YouTubeService
from .base import BasePlatformService

# Можно добавить фабрику для выбора сервиса по платформе
PLATFORM_SERVICES = {
    'spotify': SpotifyService,
    'yandex': YandexMusicService,
    'youtube': YouTubeService,
}

def get_platform_service(platform: str, db, user_id):
    cls = PLATFORM_SERVICES.get(platform)
    if not cls:
        raise ValueError(f"Unknown platform: {platform}")
    return cls(db, user_id)