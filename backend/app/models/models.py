from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, JSON
) 
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    connected_services = relationship('ConnectedService', back_populates='user')
    playlists = relationship('UserPlaylist', back_populates='user')
    favorites = relationship('UserFavorite', back_populates='user')


class ConnectedService(Base):
    __tablename__ = 'connected_services'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String, nullable=False)
    external_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    expires_at = Column(DateTime)

    user = relationship('User', back_populates='connected_services')

class UserFavorite(Base):
    __tablename__ = 'user_favorites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String, nullable=False)
    external_id = Column(String, nullable=True)  # nullable=True для обратной совместимости
    playlist_id = Column(String, nullable=False)  # для связи с плейлистом Liked Songs
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    tracks_number = Column(Integer, nullable=False)

    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='favorites')


class UserPlaylist(Base):
    __tablename__ = 'user_playlists'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)  # добавлено поле description
    source_platform = Column(String)
    is_mixed = Column(Boolean, default=False)
    external_id = Column(String)  # Spotify playlist id
    is_public = Column(Boolean, default=False)
    tracks_number = Column(Integer, nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='playlists')
    tracks = relationship('PlaylistTrack', back_populates='playlist')


class PlaylistTrack(Base):
    __tablename__ = 'playlist_tracks'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey('user_playlists.id'), nullable=False)
    platform = Column(String)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    order_index = Column(Integer)

    playlist = relationship('UserPlaylist', back_populates='tracks')
    track = relationship('Track', back_populates='playlist_tracks')

    __table_args__ = (UniqueConstraint("playlist_id", "track_id", name="uq_track_per_playlist"),)


class Track(Base):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    duration = Column(Integer)  # duration in seconds
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    availability = relationship("TrackAvailability", back_populates="track")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track")  # исправлено имя свойства для back_populates


class TrackAvailability(Base):
    __tablename__ = "tracks_availability"

    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    platform = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    url = Column(String)
    available = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, default=datetime.utcnow)

    track = relationship("Track", back_populates="availability")

    __table_args__ = (UniqueConstraint("track_id", "platform", name="uq_track_platform"),)

