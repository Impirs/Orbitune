import os
import logging
import requests

from datetime import datetime
from app.models.models import UserPlaylist, PlaylistTrack, Track, TrackAvailability, UserFavorite, ConnectedService
from sqlalchemy.orm import Session
from .base import BasePlatformService

YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

class YouTubeService(BasePlatformService):

    def __init__(self, db: Session, user_id: int):
        super().__init__(db, user_id)
        self.token = self._get_token()
        self.external_user_id = self._get_external_user_id()

    def _get_token(self):
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="youtube").first()
        if not service:
            return None
        return service.access_token

    def _refresh_token(self):
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="youtube").first()
        if not service or not service.refresh_token:
            logging.warning(f"[YOUTUBE] Нет refresh_token для user_id={self.user_id}")
            return False
        data = {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "refresh_token": service.refresh_token,
            "grant_type": "refresh_token"
        }
        resp = requests.post("https://oauth2.googleapis.com/token", data=data)
        logging.info(f"[YOUTUBE] refresh_token status={resp.status_code} body={resp.text[:500]}")
        if resp.status_code == 200:
            tokens = resp.json()
            service.access_token = tokens["access_token"]
            self.db.commit()
            self.token = tokens["access_token"]
            logging.info(f"[YOUTUBE] access_token обновлён для user_id={self.user_id}")
            return True
        else:
            logging.error(f"[YOUTUBE] Не удалось обновить access_token для user_id={self.user_id}. Ответ: {resp.text}")
            # Удаляем сервис если refresh_token невалиден
            if resp.status_code == 400 and "invalid_grant" in resp.text:
                self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="youtube").delete()
                self.db.commit()
                logging.warning(f"[YOUTUBE] ConnectedService удалён для user_id={self.user_id} из-за невалидного refresh_token")
        return False

    def _get_external_user_id(self):
        service = self.db.query(ConnectedService).filter_by(user_id=self.user_id, platform="youtube").first()
        if not service:
            return None
        return service.external_user_id

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_playlists(self, limit=50):
        if not self.token:
            return []
        playlists = []
        url = f"{YOUTUBE_API_BASE}/playlists?part=snippet,contentDetails&mine=true&maxResults=50"
        retried = False
        while url:
            resp = requests.get(url, headers=self._headers())
            logging.info(f"[YOUTUBE] get_playlists status={resp.status_code} url={url} body={resp.text[:200]}")
            if resp.status_code == 401 and not retried:
                if self._refresh_token():
                    retried = True
                    resp = requests.get(url, headers=self._headers())
                    logging.info(f"[YOUTUBE] get_playlists (after refresh) status={resp.status_code} url={url} body={resp.text[:200]}")
                else:
                    raise Exception("YouTube access token expired and refresh failed.")
            if resp.status_code != 200:
                logging.error(f"[YOUTUBE] YouTube API error: {resp.status_code} {resp.text}")
                raise Exception(f"YouTube API error: {resp.status_code} {resp.text}")
            data = resp.json()
            for pl in data.get("items", []):
                playlists.append({
                    "id": pl["id"],
                    "title": pl["snippet"]["title"],
                    "description": pl["snippet"].get("description", ""),
                    "tracks_count": pl["contentDetails"].get("itemCount", 0),
                    "cover_url": pl["snippet"].get("thumbnails", {}).get("medium", {}).get("url"),
                    "source_platform": "youtube"
                })
            nextPageToken = data.get("nextPageToken")
            if nextPageToken:
                url = f"{YOUTUBE_API_BASE}/playlists?part=snippet,contentDetails&mine=true&maxResults=50&pageToken={nextPageToken}"
            else:
                url = None
        return playlists

    def get_favorite_tracks_all(self):
        # YouTube Music "Liked songs" = playlist with title "Liked songs" or id "LL..."
        liked_playlist = self.get_liked_playlist_info()
        if not liked_playlist:
            return []
        return self.get_playlist_tracks(liked_playlist["id"])

    def sync_user_playlists_and_favorites(self):
        logging.info(f"[YOUTUBE SYNC] user_id={self.user_id} token={self.token}")
        session = self.db
        db_playlists = session.query(UserPlaylist).filter_by(user_id=self.user_id, source_platform="youtube").all()
        youtube_playlists = {pl["id"]: pl for pl in self.get_playlists()}
        logging.info(f"[YOUTUBE SYNC] Получено плейлистов из YouTube: {len(youtube_playlists)}")
        for db_pl in db_playlists:
            pl_data = youtube_playlists.get(db_pl.external_id)
            if not pl_data:
                # Плейлист был удалён на YouTube — удаляем из БД и чистим связи
                logging.info(f"[YOUTUBE SYNC] Удалён плейлист {db_pl.external_id} из БД (не найден на YouTube)")
                session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
                session.delete(db_pl)
                session.commit()
                continue
            tracks = self.get_playlist_tracks(db_pl.external_id)
            db_pl.title = pl_data["title"]
            db_pl.description = pl_data.get("description")
            db_pl.updated_at = datetime.utcnow()
            db_pl.image_url = pl_data.get("cover_url")
            db_pl.tracks_number = len(tracks)
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
                if db_track.id not in seen_track_ids:
                    session.add(PlaylistTrack(
                        playlist_id=db_pl.id,
                        platform="youtube",
                        track_id=db_track.id,
                        order_index=idx
                    ))
                    seen_track_ids.add(db_track.id)
            session.commit()
        # Сохраняем "Liked songs" как избранное
        liked = self.get_liked_playlist_info()
        if liked:
            liked_tracks = self.get_playlist_tracks(liked["id"])
            session.query(UserFavorite).filter_by(user_id=self.user_id, platform="youtube").delete()
            session.flush()
            session.add(UserFavorite(
                user_id=self.user_id,
                external_id=liked["id"],
                playlist_id=liked["id"],
                platform="youtube",
                title=liked["title"],
                description=liked.get("description"),
                tracks_number=len(liked_tracks),
                updated_at=datetime.utcnow()
            ))
            session.commit()

    def get_stats(self):
        # Можно получить имя пользователя через people/me или userinfo
        return {
            "external_user_id": self.external_user_id,
            "display_name": "YouTube User",
            "songs": 0,
            "playlists": 0,
            "subscription_type": "—",
        }

    def get_playlist_tracks(self, playlist_id, limit=100):
        # --- Получение треков для плейлиста из бд ---
        if not self.token:
            return []
        tracks = []
        url = f"{YOUTUBE_API_BASE}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults=50"
        retried = False
        while url:
            resp = requests.get(url, headers=self._headers())
            if resp.status_code == 401 and not retried:
                if self._refresh_token():
                    retried = True
                    resp = requests.get(url, headers=self._headers())
                else:
                    break
            if resp.status_code != 200:
                break
            data = resp.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                artist = snippet.get("videoOwnerChannelTitle", "")
                video_id = snippet.get("resourceId", {}).get("videoId")
                # Для YouTube Music duration и album не всегда доступны
                tracks.append({
                    "id": video_id,
                    "title": title,
                    "artist": artist,
                    "album": None,
                    "duration": None,
                    "cover_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                    "platform": "youtube"
                })
            nextPageToken = data.get("nextPageToken")
            if nextPageToken:
                url = f"{YOUTUBE_API_BASE}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={nextPageToken}"
            else:
                url = None
        return tracks

    def get_playlist_tracks_count(self, playlist_id):
        # Можно получить через get_playlists
        pls = self.get_playlists()
        for pl in pls:
            if pl["id"] == playlist_id:
                return pl.get("tracks_count", 0)
        return 0

    def get_liked_playlist_info(self):
        # Обычно id плейлиста "Понравившиеся" начинается с "LL" ("Liked videos")
        pls = self.get_playlists()
        for pl in pls:
            if pl["title"].lower() in ("liked songs", "понравившиеся", "liked videos") or pl["id"].startswith("LL"):
                return {
                    "id": pl["id"],
                    "title": pl["title"],
                    "description": pl.get("description", "YouTube Liked Tracks")
                }
        return None

    def fetch_service_temp_data(self):
        # --- Получить все плейлисты и треки через API, не трогая БД, для фильтра пользователем ---
        playlists = self.get_playlists()
        for pl in playlists:
            pl['tracks'] = self.get_playlist_tracks_with_duration(pl['id'])
        return playlists

    def get_playlist_tracks_with_duration(self, playlist_id, limit=100):
        # Получаем треки с корректным duration (YouTube API videos?part=contentDetails), ибо он не получается с композицией априори ---
        if not self.token:
            return []
        tracks = []
        video_ids = []
        url = f"{YOUTUBE_API_BASE}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults=50"
        retried = False
        while url:
            resp = requests.get(url, headers=self._headers())
            if resp.status_code == 401 and not retried:
                if self._refresh_token():
                    retried = True
                    resp = requests.get(url, headers=self._headers())
                else:
                    break
            if resp.status_code != 200:
                break
            data = resp.json()
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                artist = snippet.get("videoOwnerChannelTitle", "")
                video_id = snippet.get("resourceId", {}).get("videoId")
                video_ids.append(video_id)
                tracks.append({
                    "id": video_id,
                    "title": title,
                    "artist": artist,
                    "album": None,
                    "duration": None,  # Низкий приоритет
                    "cover_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                    "platform": "youtube"
                })
            nextPageToken = data.get("nextPageToken")
            if nextPageToken:
                url = f"{YOUTUBE_API_BASE}/playlistItems?part=snippet,contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={nextPageToken}"
            else:
                url = None
        # Получаем duration батчем, тк приоритет низкий
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            vurl = f"{YOUTUBE_API_BASE}/videos?part=contentDetails&id={','.join(batch_ids)}"
            vresp = requests.get(vurl, headers=self._headers())
            if vresp.status_code == 401:
                if self._refresh_token():
                    vresp = requests.get(vurl, headers=self._headers())
                else:
                    continue
            if vresp.status_code != 200:
                continue
            vdata = vresp.json()
            id_to_duration = {item['id']: self._parse_duration(item['contentDetails']['duration']) for item in vdata.get('items', [])}
            for t in tracks:
                if t['id'] in id_to_duration:
                    t['duration'] = id_to_duration[t['id']]
        return tracks

    def _parse_duration(self, iso_duration):
        # Преобразует ISO 8601 duration (PT4M13S) в секунды
        import re
        if not iso_duration:
            return None
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(iso_duration)
        if not match:
            return None
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def save_selected_playlists(self, playlists_data):
        session = self.db
        seen_availability = set()
        for pl in playlists_data:
            db_pl = session.query(UserPlaylist).filter_by(user_id=self.user_id, external_id=pl["id"], source_platform="youtube").first()
            tracks = pl.get("tracks", [])
            if not db_pl:
                db_pl = UserPlaylist(
                    user_id=self.user_id,
                    title=pl["title"],
                    description=pl.get("description"),
                    source_platform="youtube",
                    external_id=pl["id"],
                    updated_at=datetime.utcnow(),
                    image_url=pl.get("cover_url"),
                    is_public=True,
                    tracks_number=len(tracks)
                )
                session.add(db_pl)
                session.flush()
            else:
                db_pl.title = pl["title"]
                db_pl.description = pl.get("description")
                db_pl.updated_at = datetime.utcnow()
                db_pl.image_url = pl.get("cover_url")
                db_pl.tracks_number = len(tracks)
            session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
            seen_track_ids = set()
            for idx, t in enumerate(tracks):
                # --- Tracks: Добавляем все треки при появлении в первый раз, дубликаты пропускаем ---
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
                # --- TrackAvailability: пропускаем, если уже добавляли в этой сессии ---
                track_avail_key = (db_track.id, "youtube")
                if track_avail_key not in seen_availability:
                    if not session.query(TrackAvailability).filter_by(track_id=db_track.id, platform="youtube").first():
                        avail = TrackAvailability(
                            track_id=db_track.id,
                            platform="youtube",
                            external_id=t["id"],
                            url=None,
                            available=True
                        )
                        session.add(avail)
                    seen_availability.add(track_avail_key)
                # --- PlaylistTrack: если трек уже был добавлен в этот плейлист, пропускаем (оставляем только первый order_index) ---
                if db_track.id not in seen_track_ids:
                    session.add(PlaylistTrack(
                        playlist_id=db_pl.id,
                        platform="youtube",
                        track_id=db_track.id,
                        order_index=idx
                    ))
                    seen_track_ids.add(db_track.id)
            session.commit()
        # Сохраняем "Liked songs" как избранное
        liked = self.get_liked_playlist_info()
        if liked:
            liked_tracks = self.get_playlist_tracks(liked["id"])
            session.query(UserFavorite).filter_by(user_id=self.user_id, platform="youtube").delete()
            session.flush()
            session.add(UserFavorite(
                user_id=self.user_id,
                external_id=liked["id"],
                playlist_id=liked["id"],
                platform="youtube",
                title=liked["title"],
                description=liked.get("description"),
                tracks_number=len(liked_tracks),
                updated_at=datetime.utcnow()
            ))
            session.commit()

    def delete_playlist_by_external_id(self, external_id):
        # Удаляет плейлист пользователя по external_id (YouTube id) и user_id, а также все PlaylistTrack для этого плейлиста.
        session = self.db
        db_pl = session.query(UserPlaylist).filter_by(user_id=self.user_id, external_id=external_id, source_platform="youtube").first()
        if db_pl:
            session.query(PlaylistTrack).filter(PlaylistTrack.playlist_id == db_pl.id).delete()
            session.delete(db_pl)
            session.commit()
