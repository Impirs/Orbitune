import requests
from .base import BasePlatformService
from app.models.models import ConnectedService
from sqlalchemy.orm import Session
from datetime import datetime

class YandexMusicService(BasePlatformService):
    BASE_URL = "https://api.music.yandex.net"

    def __init__(self, db: Session, user_id: int):
        super().__init__(db, user_id)
        self.token = self._get_token()

    def _get_token(self):
        # Получаем xtoken для Яндекс.Музыки из ConnectedService (теперь только ручной ввод)
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="yandex-music").first()
        if not service:
            return None
        return service.access_token

    def _headers(self):
        return {"Authorization": f"OAuth {self.token}"}

    def get_user_profile(self):
        resp = requests.get(f"{self.BASE_URL}/account/status", headers=self._headers())
        if resp.status_code != 200:
            return None
        return resp.json().get("result", {})

    def get_playlists(self, limit=100):
        resp = requests.get(f"{self.BASE_URL}/users/{self.user_id}/playlists/list", headers=self._headers())
        if resp.status_code != 200:
            return []
        playlists = resp.json().get("result", [])
        return [
            {
                "id": pl["kind"],
                "title": pl["title"],
                "description": pl.get("description", ""),
                "tracks_count": pl.get("trackCount", 0),
                "cover_url": pl["cover"]['uri'] if pl.get("cover") else None,
                "source_platform": "yandex"
            }
            for pl in playlists
        ]

    def get_favorite_tracks_all(self):
        # Получить все треки из "Моей музыки" (лайкнутые)
        tracks = []
        offset = 0
        page_size = 100
        while True:
            url = f"{self.BASE_URL}/users/{self.user_id}/likes/tracks?limit={page_size}&offset={offset}"
            resp = requests.get(url, headers=self._headers())
            if resp.status_code != 200:
                break
            items = resp.json().get("result", {}).get("tracks", [])
            if not items:
                break
            tracks.extend([
                {
                    "id": t["id"],
                    "title": t["title"],
                    "artist": t["artists"][0]["name"] if t.get("artists") else "",
                    "album": t.get("albums", [{}])[0].get("title", "") if t.get("albums") else "",
                    "duration": t.get("durationMs", 0) // 1000,
                    "cover_url": None,  # Можно доработать
                    "platform": "yandex"
                }
                for t in items
            ])
            if len(items) < page_size:
                break
            offset += page_size
        return tracks

    def sync_user_playlists_and_favorites(self):
        import logging
        from app.models.models import UserPlaylist, UserFavorite, Track, PlaylistTrack, TrackAvailability
        logging.info(f"[YANDEX SYNC] user_id={self.user_id} token={self.token}")
        playlists = self.get_playlists()
        logging.info(f"[YANDEX SYNC] Получено плейлистов из Yandex: {len(playlists)}")
        session = self.db
        liked = self.get_liked_playlist_info()
        # Сохраняем Liked Songs в user_favorites (удаляем старый)
        session.query(UserFavorite).filter_by(user_id=self.user_id, platform="yandex").delete()
        session.flush()
        session.add(UserFavorite(
            user_id=self.user_id,
            external_id=liked["id"],
            playlist_id=liked["id"],
            platform="yandex",
            title=liked["title"],
            description=liked.get("description"),
            tracks_number=len(self.get_favorite_tracks_all()),
            updated_at=datetime.utcnow()
        ))
        logging.info(f"[YANDEX SYNC] Сохранён Liked Songs: {liked['id']}")
        # Получаем все id плейлистов, которые есть на сервисе
        yandex_ids = set(str(pl["id"]) for pl in playlists if pl["title"].lower() != "моя музыка")
        logging.info(f"[YANDEX SYNC] Yandex playlist ids: {yandex_ids}")
        # Удаляем только связи PlaylistTrack для плейлистов, которых больше нет на сервисе
        db_playlists = session.query(UserPlaylist).filter(
            UserPlaylist.user_id == self.user_id,
            UserPlaylist.source_platform == "yandex"
        ).all()
        for db_pl in db_playlists:
            if str(db_pl.external_id) not in yandex_ids:
                session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
        session.flush()
        # Обновляем или добавляем плейлисты и их треки
        for pl in playlists:
            if pl["title"].lower() == "моя музыка":
                continue
            tracks = self.get_playlist_tracks(pl["id"])
            db_pl = session.query(UserPlaylist).filter_by(user_id=self.user_id, external_id=str(pl["id"]), source_platform="yandex").first()
            if not db_pl:
                db_pl = UserPlaylist(
                    user_id=self.user_id,
                    title=pl["title"],
                    description=pl.get("description"),
                    source_platform="yandex",
                    external_id=str(pl["id"]),
                    updated_at=datetime.utcnow(),
                    image_url=pl.get("cover_url"),
                    is_public=True,
                    tracks_number=len(tracks)
                )
                session.add(db_pl)
                session.flush()
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
                track_avail_key = (db_track.id, "yandex")
                if not hasattr(self, '_seen_availability'):
                    self._seen_availability = set()
                if track_avail_key in self._seen_availability:
                    continue
                self._seen_availability.add(track_avail_key)
                avail = session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="yandex").first()
                if not avail:
                    avail = TrackAvailability(
                        track_id=db_track.id,
                        platform="yandex",
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
                        platform="yandex",
                        track_id=db_track.id,
                        order_index=idx
                    ))
                    seen_track_ids.add(db_track.id)
            session.commit()
        # --- Liked Songs ---
        liked_tracks = self.get_favorite_tracks_all()
        liked_playlist = session.query(UserPlaylist).filter_by(
            user_id=self.user_id,
            source_platform="yandex",
            external_id=liked["id"]
        ).first()
        if not liked_playlist:
            liked_playlist = UserPlaylist(
                user_id=self.user_id,
                title=liked["title"],
                description=liked.get("description"),
                source_platform="yandex",
                external_id=liked["id"],
                updated_at=datetime.utcnow(),
                image_url=None,
                is_public=True,
                tracks_number=len(liked_tracks)
            )
            session.add(liked_playlist)
            session.commit()
        else:
            liked_playlist.updated_at = datetime.utcnow()
            liked_playlist.is_public = True
            liked_playlist.tracks_number = len(liked_tracks)
        session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == liked_playlist.id).delete()
        seen_track_ids = set()
        for idx, t in enumerate(liked_tracks):
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
            track_avail_key = (db_track.id, "yandex")
            if not hasattr(self, '_seen_availability'):
                self._seen_availability = set()
            if track_avail_key in self._seen_availability:
                continue
            self._seen_availability.add(track_avail_key)
            avail = session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="yandex").first()
            if not avail:
                avail = TrackAvailability(
                    track_id=db_track.id,
                    platform="yandex",
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
                    playlist_id=liked_playlist.id,
                    platform="yandex",
                    track_id=db_track.id,
                    order_index=idx
                ))
                seen_track_ids.add(db_track.id)
        fav = session.query(UserFavorite).filter_by(user_id=self.user_id, platform="yandex").first()
        if fav:
            fav.tracks_number = len(liked_tracks)
        session.commit()
        logging.info(f"[YANDEX SYNC] Коммит завершён для user_id={self.user_id}")
        if hasattr(self, '_seen_availability'):
            del self._seen_availability

    def get_stats(self):
        profile = self.get_user_profile() or {}
        return {
            "external_user_id": profile.get("uid"),
            "display_name": profile.get("login"),
            "subscription_type": profile.get("plus", False),
        }

    def get_playlist_tracks(self, playlist_id, limit=100):
        url = f"{self.BASE_URL}/users/{self.user_id}/playlists/{playlist_id}/tracks?page-size={limit}"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return []
        items = resp.json().get("result", {}).get("tracks", [])
        return [
            {
                "id": t["id"],
                "title": t["title"],
                "artist": t["artists"][0]["name"] if t.get("artists") else "",
                "album": t.get("albums", [{}])[0].get("title", "") if t.get("albums") else "",
                "duration": t.get("durationMs", 0) // 1000,
                "cover_url": None,  # Можно доработать
                "platform": "yandex"
            }
            for t in items
        ]

    def get_playlist_tracks_count(self, playlist_id):
        url = f"{self.BASE_URL}/users/{self.user_id}/playlists/{playlist_id}"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return 0
        return resp.json().get("result", {}).get("trackCount", 0)

    def get_liked_playlist_info(self):
        return {
            "id": f"yandex:liked:{self.user_id}",
            "title": "Моя музыка",
            "description": "Yandex Liked Tracks"
        }
