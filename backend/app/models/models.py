from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

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


class Track(Base):
    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    duration = Column(Integer)  # duration in seconds
    cover_url = Column(String)
    external_ids = Column(JSONB)
    platforms_available = Column(JSONB)

    playlist_tracks = relationship('PlaylistTrack', back_populates='track')


class UserPlaylist(Base):
    __tablename__ = 'user_playlists'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    source_platform = Column(String)
    is_mixed = Column(Boolean, default=False)
    external_id = Column(String)  # Spotify playlist id

    user = relationship('User', back_populates='playlists')
    tracks = relationship('PlaylistTrack', back_populates='playlist')


class PlaylistTrack(Base):
    __tablename__ = 'playlist_tracks'
    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey('user_playlists.id'), nullable=False)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False)
    platform = Column(String)
    order = Column(Integer)

    playlist = relationship('UserPlaylist', back_populates='tracks')
    track = relationship('Track', back_populates='playlist_tracks')


class UserFavorite(Base):
    __tablename__ = 'user_favorites'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    playlist_id = Column(String, nullable=False)  # Spotify playlist id (for liked songs)
    external_id = Column(String)
    title = Column(String)
    description = Column(String)
    platform = Column(String)

    user = relationship('User', back_populates='favorites')
