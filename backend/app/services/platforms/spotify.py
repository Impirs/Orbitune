import requests
from app.models.models import ConnectedService
from sqlalchemy.orm import Session
from datetime import datetime
from .base import BasePlatformService

class SpotifyService(BasePlatformService):
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, db: Session, user_id: int):
        super().__init__(db, user_id)
        self.token = self._get_token()

    def _get_token(self):
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="spotify").first()
        if not service:
            return None
        return service.access_token

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _refresh_token(self):
        import os
        import logging
        from app.models.models import ConnectedService
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="spotify").first()
        if not service or not service.refresh_token:
            logging.warning(f"[SPOTIFY] Нет refresh_token для user_id={self.user_id}")
            return False
        data = {
            "grant_type": "refresh_token",
            "refresh_token": service.refresh_token,
            "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
            "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
        }
        resp = requests.post("https://accounts.spotify.com/api/token", data=data)
        logging.info(f"[SPOTIFY] refresh_token status={resp.status_code} body={resp.text[:200]}")
        if resp.status_code == 200:
            tokens = resp.json()
            service.access_token = tokens["access_token"]
            self.db.commit()
            self.token = tokens["access_token"]
            logging.info(f"[SPOTIFY] access_token обновлён для user_id={self.user_id}")
            return True
        logging.error(f"[SPOTIFY] Не удалось обновить access_token для user_id={self.user_id}")
        return False

    def get_user_profile(self):
        import logging
        resp = requests.get(f"{self.BASE_URL}/me", headers=self._headers())
        logging.info(f"[SPOTIFY] get_user_profile status={resp.status_code} body={resp.text[:200]}")
        if resp.status_code == 401:
            if self._refresh_token():
                resp = requests.get(f"{self.BASE_URL}/me", headers=self._headers())
                logging.info(f"[SPOTIFY] get_user_profile (after refresh) status={resp.status_code} body={resp.text[:200]}")
        if resp.status_code != 200:
            return None
        return resp.json()

    def get_playlists(self, limit=50):
        import logging
        playlists = []
        offset = 0
        while True:
            url = f"{self.BASE_URL}/me/playlists?limit={limit}&offset={offset}"
            resp = requests.get(url, headers=self._headers())
            logging.info(f"[SPOTIFY] get_playlists status={resp.status_code} url={url} body={resp.text[:200]}")
            if resp.status_code == 401:
                if self._refresh_token():
                    resp = requests.get(url, headers=self._headers())
                    logging.info(f"[SPOTIFY] get_playlists (after refresh) status={resp.status_code} url={url} body={resp.text[:200]}")
            if resp.status_code != 200:
                break
            items = resp.json().get("items", [])
            if not items:
                break
            for pl in items:
                playlists.append({
                    "id": pl["id"],
                    "title": pl["name"],
                    "description": pl.get("description", ""),
                    "tracks_count": pl["tracks"]["total"],
                    "cover_url": pl["images"][0]["url"] if pl["images"] else None,
                    "source_platform": "spotify"
                })
            if len(items) < limit:
                break
            offset += limit
        return playlists

    def get_favorite_tracks_all(self):
        tracks = []
        offset = 0
        limit = 50
        while True:
            url = f"{self.BASE_URL}/me/tracks?limit={limit}&offset={offset}"
            resp = requests.get(url, headers=self._headers())
            if resp.status_code != 200:
                break
            items = resp.json().get("items", [])
            if not items:
                break
            tracks.extend([
                {
                    "id": item["track"]["id"],
                    "title": item["track"]["name"],
                    "artist": ", ".join([a["name"] for a in item["track"]["artists"]]),
                    "album": item["track"]["album"]["name"],
                    "duration": item["track"]["duration_ms"] // 1000,
                    "cover_url": item["track"]["album"]["images"][0]["url"] if item["track"]["album"]["images"] else None,
                    "platform": "spotify"
                }
                for item in items
            ])
            if len(items) < limit:
                break
            offset += limit
        return tracks

    def get_favorite_tracks(self, limit=50):
        return self.get_favorite_tracks_all()

    def get_stats(self):
        try:
            profile = self.get_user_profile() or {}
            songs_count = self.get_liked_songs_count()
            playlists_count = self.get_playlists_count()
            return {
                "external_user_id": profile.get("id"),
                "display_name": profile.get("display_name"),
                "songs": songs_count,
                "playlists": playlists_count,
                "subscription_type": profile.get("product", "—"),
            }
        except Exception as e:
            import logging
            logging.error(f"Error in SpotifyService.get_stats: {str(e)}")
            return {
                "external_user_id": "Error retrieving data",
                "display_name": "Unknown",
                "error": str(e)
            }

    def sync_user_playlists_and_favorites(self):
        # ...скопировать реализацию из старого platforms.py...
        pass

    def get_liked_songs_count(self):
        url = f"{self.BASE_URL}/me/tracks?limit=1"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return 0
        return resp.json().get("total", 0)

    def get_playlists_count(self):
        playlists = self.get_playlists()
        return len([pl for pl in playlists if pl["title"].lower() != "liked songs"])

    def get_liked_playlist_info(self):
        profile = self.get_user_profile() or {}
        return {
            "id": f"spotify:liked:{profile.get('id')}",
            "title": "Liked Songs",
            "description": "Spotify Liked Songs playlist",
        }

    def get_playlist_tracks(self, playlist_id, limit=100):
        tracks = []
        offset = 0
        while True:
            url = f"{self.BASE_URL}/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
            resp = requests.get(url, headers=self._headers())
            if resp.status_code != 200:
                break
            items = resp.json().get("items", [])
            if not items:
                break
            for item in items:
                t = item.get("track")
                if not t:
                    continue
                tracks.append({
                    "id": t["id"],
                    "title": t["name"],
                    "artist": ", ".join([a["name"] for a in t["artists"]]),
                    "album": t["album"]["name"],
                    "duration": t["duration_ms"] // 1000,
                    "cover_url": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
                    "platform": "spotify"
                })
            if len(items) < limit:
                break
            offset += limit
        return tracks

    def get_playlist_tracks_count(self, playlist_id):
        url = f"{self.BASE_URL}/playlists/{playlist_id}"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return 0
        return resp.json().get("tracks", {}).get("total", 0)
