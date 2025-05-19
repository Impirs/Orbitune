from .base import BasePlatformService

class YouTubeService(BasePlatformService):
    """Заглушка для YouTube Music. Реализация будет позже."""
    def get_playlists(self):
        return []

    def get_favorite_tracks_all(self):
        return []

    def sync_user_playlists_and_favorites(self):
        pass

    def get_stats(self):
        return {}

    def get_playlist_tracks(self, playlist_id, limit=100):
        return []

    def get_playlist_tracks_count(self, playlist_id):
        return 0

    def get_liked_playlist_info(self):
        return {}
