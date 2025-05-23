import { defineStore } from 'pinia';
import axios from 'axios';

export const useServicesStore = defineStore('services', {
  state: () => ({
    playlists: {}, // { [platform]: Playlist[] }
    favorites: {}, // { [platform]: Track[] }
    favoritesTotal: 0,
    loading: false,
    error: '',
  }),
  actions: {
    async fetchPlaylists(userId, platform) {
      if (!userId || !platform) {
        this.error = 'User ID or platform missing';
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/playlists', { params: { user_id: userId, platform }, withCredentials: true });
        this.playlists[platform] = res.data.playlists || [];
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load playlists for ${platform}`;
      } finally {
        this.loading = false;
      }
    },
    async fetchPlaylistTracks(userId, playlistId, platform) {
      if (!userId || !playlistId || !platform) return;
      const pl = this.playlists[platform]?.find(p => String(p.id) === String(playlistId));
      if (pl && pl.tracks && pl.tracks.length > 0) return;
      try {
        const res = await axios.get(`/playlists/${playlistId}/tracks`, { params: { platform, user_id: userId }, withCredentials: true });
        this.playlists[platform] = this.playlists[platform].map(pl =>
          String(pl.id) === String(playlistId)
            ? { ...pl, tracks: res.data.tracks || [] }
            : pl
        );
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load tracks for playlist ${playlistId}`;
      }
    },
    async fetchFavorites(userId, platform) {
      if (!userId || !platform) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: userId, platform }, withCredentials: true });
        this.favorites[platform] = res.data.tracks || [];
        this.favoritesTotal = res.data.tracks_count || (this.favorites[platform] ? this.favorites[platform].length : 0);
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load favorites for ${platform}`;
      } finally {
        this.loading = false;
      }
    },
    async fetchFavoritesLazy(userId, offset = 0, limit = 50, platform) {
      if (!userId || !platform) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: userId, offset, limit, platform }, withCredentials: true });
        if (offset === 0) {
          this.favorites[platform] = res.data.tracks || [];
        } else {
          this.favorites[platform] = [...(this.favorites[platform] || []), ...(res.data.tracks || [])];
        }
        this.favoritesTotal = res.data.tracks_count || (this.favorites[platform] ? this.favorites[platform].length : 0);
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load favorites for ${platform}`;
      } finally {
        this.loading = false;
      }
    },
    async fetchFavoritesPlaylistId(userId, platform) {
      if (!userId || !platform) return null;
      try {
        const res = await axios.get('/favorites', { params: { user_id: userId, platform }, withCredentials: true });
        return res.data?.playlist?.external_id || null;
      } catch (e) {
        return null;
      }
    },
    async disconnectService(userId, platform) {
      if (!userId || !platform) return;
      try {
        await axios.delete('/connected_services', { params: { user_id: userId, platform }, withCredentials: true });
        // После успешного отключения можно очистить локальные данные по платформе
        // if (this.playlists[platform]) delete this.playlists[platform];
        // if (this.favorites[platform]) delete this.favorites[platform];
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to disconnect service ${platform}`;
      }
    },
  }
});
