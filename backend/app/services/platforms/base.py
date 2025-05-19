# Base class for all platform services
from sqlalchemy.orm import Session

class BasePlatformService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_playlists(self):
        raise NotImplementedError

    def get_favorite_tracks_all(self):
        raise NotImplementedError

    def sync_user_playlists_and_favorites(self):
        raise NotImplementedError

    def get_stats(self):
        raise NotImplementedError

    def get_playlist_tracks(self, playlist_id, limit=100):
        raise NotImplementedError

    def get_playlist_tracks_count(self, playlist_id):
        raise NotImplementedError

    def get_liked_playlist_info(self):
        raise NotImplementedError
