import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false,
    connectedServices: [],
    playlists: [],
    favorites: [],
    loading: false, // глобальный лоадер
    error: '',     // глобальная ошибка
    lastSelectedPlaylist: null, // id последнего выбранного плейлиста
    favoritesPlaylistId: null, // id плейлиста избранного (user_playlists.id)
  }),
  actions: {
    async syncSpotify() {
      if (!this.currentUser) return;
      try {
        await fetch(`/connected_services/sync?user_id=${this.currentUser.id}`, { method: 'POST' });
      } catch (e) {
        // ignore
      }
    },
    async login(email, password) {
      try {
        console.log('[LOGIN] Sending:', { email, password });
        const res = await axios.post('/auth/login', { email, password }, { withCredentials: true });
        console.log('[LOGIN] Response:', res.data);
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
        this.saveSession();
        await this.fetchConnectedServices();
        console.log('[SYNC] Calling syncSpotify for user', this.currentUser?.id);
        await this.syncSpotify();
        await this.fetchPlaylists();
        await this.fetchFavoritesFull();
        return { ok: true };
      } catch (e) {
        console.error('[LOGIN] Error object:', e);
        let msg = 'Unknown error';
        if (e?.response?.data?.detail) msg = e.response.data.detail;
        else if (e?.response?.data) msg = JSON.stringify(e.response.data);
        else if (e?.message) msg = e.message;
        return { ok: false, error: msg };
      }
    },
    async register(email, password) {
      try {
        console.log('[REGISTER] Sending:', { email, password });
        const res = await axios.post('/auth/register', { email, password }, { withCredentials: true });
        console.log('[REGISTER] Response:', res.data);
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
        this.saveSession();
        await this.fetchConnectedServices();
        await this.fetchPlaylists();
        await this.fetchFavoritesFull();
        return { ok: true };
      } catch (e) {
        console.error('[REGISTER] Error object:', e);
        let msg = 'Unknown error';
        if (e?.response?.data?.detail) msg = e.response.data.detail;
        else if (e?.response?.data) msg = JSON.stringify(e.response.data);
        else if (e?.message) msg = e.message;
        return { ok: false, error: msg };
      }
    },
    logout() {
      this.currentUser = null;
      this.isLoggedIn = false;
      this.connectedServices = [];
      this.playlists = [];
      this.favorites = [];
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
      axios.post('/auth/logout', {}, { withCredentials: true });
    },
    async fetchConnectedServices() {
      if (!this.currentUser) return;
      if (this.connectedServices && this.connectedServices.length > 0) {
        console.log('[fetchConnectedServices] Connected services already loaded, skip request');
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        console.log('[fetchConnectedServices] Запрос сервисов...');
        const res = await axios.get('/connected_services', { params: { user_id: this.currentUser.id }, withCredentials: true });
        this.connectedServices = res.data;
        console.log('[fetchConnectedServices] Получено сервисов:', this.connectedServices.length);
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load services';
        console.error('[fetchConnectedServices] Ошибка:', e);
      } finally {
        this.loading = false;
      }
    },
    async fetchPlaylists() {
      if (!this.currentUser || !this.currentUser.id) {
        this.error = 'User not logged in or user_id missing';
        return;
      }
      if (this.playlists && this.playlists.spotify && this.playlists.spotify.length > 0) {
        console.log('[fetchPlaylists] Playlists already loaded, skip request');
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        console.log('[fetchPlaylists] Запрос плейлистов...');
        const res = await axios.get('/playlists', { params: { user_id: this.currentUser.id }, withCredentials: true });
        const basePlaylists = res.data.playlists || [];
        // Для каждого плейлиста сразу подгружаем треки из БД по внутреннему id
        const playlistsWithTracks = await Promise.all(basePlaylists.map(async (pl) => {
          try {
            const tracksRes = await axios.get(`/playlists/${pl.id}/tracks`, { withCredentials: true });
            return { ...pl, tracks: tracksRes.data.tracks || [], tracks_count: tracksRes.data.tracks_count };
          } catch (e) {
            return { ...pl, tracks: [], tracks_count: 0 };
          }
        }));
        this.playlists = { spotify: playlistsWithTracks };
        console.log('[fetchPlaylists] Получено плейлистов:', playlistsWithTracks.length, playlistsWithTracks.map(p => p.id));
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load playlists';
        console.error('[fetchPlaylists] Error:', e);
      } finally {
        this.loading = false;
      }
    },
    async fetchTracksCountBatch(ids) {
      if (!ids || ids.length === 0) return;
      console.log('[fetchTracksCountBatch] Отправка ids:', ids);
      try {
        const res = await axios.post('/playlists/tracks_count_batch', { ids }, { withCredentials: true });
        console.log('[fetchTracksCountBatch] Ответ сервера:', res.data);
        if (res.data && res.data.counts) {
          console.log('[fetchTracksCountBatch] counts:', res.data.counts);
          this.playlists.spotify = this.playlists.spotify.map(pl => ({
            ...pl,
            tracks_count: res.data.counts[pl.id] ?? undefined
          }));
        }
      } catch (e) {
        console.error('[fetchTracksCountBatch] Ошибка:', e);
      }
    },
    // Ленивая подгрузка избранных треков
    async fetchFavoritesLazy(offset = 0, limit = 50) {
      if (!this.currentUser || !this.currentUser.id) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id, offset, limit }, withCredentials: true });
        if (offset === 0) {
          this.favorites = res.data.tracks || [];
        } else {
          this.favorites = [...this.favorites, ...(res.data.tracks || [])];
        }
        this.favoritesTotal = res.data.tracks_count || this.favorites.length;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load favorites';
      } finally {
        this.loading = false;
      }
    },
    async fetchFavoritesFull() {
      if (!this.currentUser || !this.currentUser.id) return;
      if (this.favorites && this.favorites.length > 0) {
        console.log('[fetchFavoritesFull] Favorites already loaded, skip request');
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        console.log('[fetchFavoritesFull] Запрос избранных треков...');
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id }, withCredentials: true });
        this.favorites = res.data.tracks || [];
        this.favoritesTotal = res.data.tracks_count || this.favorites.length;
        console.log('[fetchFavoritesFull] Получено избранных:', this.favorites.length);
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load favorites';
        console.error('[fetchFavoritesFull] Ошибка:', e);
      } finally {
        this.loading = false;
      }
    },
    async fetchFavoritesPlaylistId() {
      // Получаем user_favorites для текущего пользователя и платформы spotify
      if (!this.currentUser || !this.currentUser.id) return;
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id }, withCredentials: true });
        // В ответе playlist.id — это external_id (user_favorites.playlist_id)
        const externalId = res.data?.playlist?.id;
        if (!externalId) return;
        // Теперь ищем user_playlists с этим external_id
        const plRes = await axios.get('/playlists', { params: { user_id: this.currentUser.id }, withCredentials: true });
        const found = (plRes.data.playlists || []).find(pl => String(pl.external_id) === String(externalId));
        if (found) {
          this.favoritesPlaylistId = found.id;
        }
      } catch (e) {
        // ignore
      }
    },
    async initialize() {
      const user = localStorage.getItem('currentUser');
      const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
      if (user && loggedIn) {
        try {
          this.currentUser = JSON.parse(user);
        } catch {
          this.currentUser = null;
        }
        this.isLoggedIn = true;
        this.loading = true;
        // Параллельно загружаем все основные данные
        const promises = [];
        if (!this.playlists || Object.keys(this.playlists).length === 0) {
          promises.push(this.fetchPlaylists());
        }
        if (!this.favorites || this.favorites.length === 0) {
          promises.push(this.fetchFavoritesFull());
        }
        if (!this.connectedServices || this.connectedServices.length === 0) {
          promises.push(this.fetchConnectedServices());
        }
        promises.push(this.fetchFavoritesPlaylistId());
        await Promise.all(promises);
        this.loading = false;
        console.log('[initialize] Все основные данные загружены');
      }
    },
    saveSession() {
      localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
      localStorage.setItem('isLoggedIn', 'true');
    }
  }
});
