import requests
from app.models.models import ConnectedService
from sqlalchemy.orm import Session
from datetime import datetime

class SpotifyService:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
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
        # Получить все избранные треки пользователя (Liked Songs) с помощью пагинации
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
        # Для обратной совместимости, но теперь возвращает все треки
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
        import logging
        from app.models.models import UserPlaylist, UserFavorite, Track, PlaylistTrack, TrackAvailability
        logging.info(f"[SYNC] user_id={self.user_id} token={self.token}")
        playlists = self.get_playlists()
        logging.info(f"[SYNC] Получено плейлистов из Spotify: {len(playlists)}")
        session = self.db
        liked = self.get_liked_playlist_info()
        # Сохраняем Liked Songs в user_favorites (удаляем старый)
        session.query(UserFavorite).filter_by(user_id=self.user_id, platform="spotify").delete()
        session.flush()
        session.add(UserFavorite(
            user_id=self.user_id,
            external_id=liked["id"],
            playlist_id=liked["id"],
            platform="spotify",
            title=liked["title"],
            description=liked.get("description"),
            tracks_number=len(self.get_favorite_tracks_all()),
            updated_at=datetime.utcnow()
        ))
        logging.info(f"[SYNC] Сохранён Liked Songs: {liked['id']}")
        # Получаем все id плейлистов, которые есть на сервисе
        spotify_ids = set(pl["id"] for pl in playlists if pl["title"].lower() != "liked songs")
        logging.info(f"[SYNC] Spotify playlist ids: {spotify_ids}")
        # Удаляем только связи PlaylistTrack для плейлистов, которых больше нет на сервисе
        db_playlists = session.query(UserPlaylist).filter(
            UserPlaylist.user_id == self.user_id,
            UserPlaylist.source_platform == "spotify"
        ).all()
        for db_pl in db_playlists:
            if db_pl.external_id not in spotify_ids:
                # Удаляем только связи PlaylistTrack
                session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
        session.flush()
        # Обновляем или добавляем плейлисты и их треки
        for pl in playlists:
            if pl["title"].lower() == "liked songs":
                continue
            tracks = self.get_playlist_tracks(pl["id"])
            db_pl = session.query(UserPlaylist).filter_by(user_id=self.user_id, external_id=pl["id"], source_platform="spotify").first()
            if not db_pl:
                # Если плейлист не найден в базе, создаём его
                db_pl = UserPlaylist(
                    user_id=self.user_id,
                    title=pl["title"],
                    description=pl.get("description"),
                    source_platform="spotify",
                    external_id=pl["id"],
                    updated_at=datetime.utcnow(),
                    image_url=pl.get("cover_url"),
                    is_public=True,
                    tracks_number=len(tracks)
                )
                session.add(db_pl)
                session.flush()
            # Удаляем старые связи PlaylistTrack для этого плейлиста (делаем только один раз перед циклом)
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
                # TrackAvailability (обработка дубликатов на уровне сессии)
                track_avail_key = (db_track.id, "spotify")
                if not hasattr(self, '_seen_availability'):
                    self._seen_availability = set()
                if track_avail_key in self._seen_availability:
                    continue  # уже обработан в этой сессии
                self._seen_availability.add(track_avail_key)
                avail = session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="spotify").first()
                if not avail:
                    avail = TrackAvailability(
                        track_id=db_track.id,
                        platform="spotify",
                        external_id=t["id"],
                        url=None,
                        available=True
                    )
                    session.add(avail)
                else:
                    avail.external_id = t["id"]
                    avail.available = True
                    avail.last_checked_at = datetime.utcnow()
                # PlaylistTrack (добавляем только если такого track_id ещё нет для этого плейлиста)
                if db_track.id not in seen_track_ids:
                    session.add(PlaylistTrack(
                        playlist_id=db_pl.id,
                        platform="spotify",
                        track_id=db_track.id,
                        order_index=idx
                    ))
                    seen_track_ids.add(db_track.id)
            session.commit()
        # --- Liked Songs ---
        liked_tracks = self.get_favorite_tracks_all()
        liked_playlist = session.query(UserPlaylist).filter_by(
            user_id=self.user_id,
            source_platform="spotify",
            external_id=liked["id"]
        ).first()
        if not liked_playlist:
            liked_playlist = UserPlaylist(
                user_id=self.user_id,
                title=liked["title"],
                description=liked.get("description"),
                source_platform="spotify",
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
        # Удаляем старые связи PlaylistTrack для Liked Songs
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
            track_avail_key = (db_track.id, "spotify")
            if not hasattr(self, '_seen_availability'):
                self._seen_availability = set()
            if track_avail_key in self._seen_availability:
                continue
            self._seen_availability.add(track_avail_key)
            avail = session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="spotify").first()
            if not avail:
                avail = TrackAvailability(
                    track_id=db_track.id,
                    platform="spotify",
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
                    platform="spotify",
                    track_id=db_track.id,
                    order_index=idx
                ))
                seen_track_ids.add(db_track.id)
        # Обновляем количество треков в user_favorites
        fav = session.query(UserFavorite).filter_by(user_id=self.user_id, platform="spotify").first()
        if fav:
            fav.tracks_number = len(liked_tracks)
        session.commit()
        logging.info(f"[SYNC] Коммит завершён для user_id={self.user_id}")
        # После синхронизации сбрасываем set
        if hasattr(self, '_seen_availability'):
            del self._seen_availability

    def get_liked_songs_count(self):
        # Получить количество песен в Liked Songs
        url = f"{self.BASE_URL}/me/tracks?limit=1"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return 0
        return resp.json().get("total", 0)

    def get_playlists_count(self):
        # Получить количество плейлистов пользователя (без Liked Songs)
        playlists = self.get_playlists()
        return len([pl for pl in playlists if pl["title"].lower() != "liked songs"])

    def get_liked_playlist_info(self):
        """
        Возвращает информацию о плейлисте Liked Songs пользователя Spotify.
        """
        profile = self.get_user_profile() or {}
        return {
            "id": f"spotify:liked:{profile.get('id')}",
            "title": "Liked Songs",
            "description": "Spotify Liked Songs playlist",
        }

    def get_playlist_tracks(self, playlist_id, limit=100):
        # Получить все треки плейлиста по его id (с пагинацией)
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
        # Получить количество треков в плейлисте по его id
        url = f"{self.BASE_URL}/playlists/{playlist_id}"
        resp = requests.get(url, headers=self._headers())
        if resp.status_code != 200:
            return 0
        return resp.json().get("tracks", {}).get("total", 0)
