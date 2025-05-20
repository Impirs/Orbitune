import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false,
    connectedServices: [],
    playlists: {}, // теперь объект с ключами-платформами
    favorites: {}, // избранное по платформам
    loading: false, // глобальный лоадер
    error: '',     // глобальная ошибка
    lastSelectedPlaylist: null, // id последнего выбранного плейлиста
    favoritesPlaylistExternalId: null, // id плейлиста избранного (user_playlists.id)
    loginStage: '', // этап загрузки при логине/регистрации
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
      this.loginStage = 'Sending requests...';
      try {
        const t0 = performance.now();
        const res = await axios.post('/auth/login', { email, password }, { withCredentials: true });
        const t1 = performance.now();
        console.log(`[LOGIN] Ответ от /auth/login получен за ${(t1 - t0).toFixed(1)} мс`, res.data);
        this.loginStage = '';
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
        this.saveSession();
        // Сразу возвращаем успех, UI становится доступен мгновенно
        setTimeout(() => { this.loginStage = ''; }, 100);
        // Параллельно грузим все данные, не блокируя UI
        setTimeout(() => {
          Promise.allSettled([
            this.fetchConnectedServices(),
            this.fetchPlaylists(),
            this.fetchFavoritesFull(),
            this.fetchFavoritesPlaylistId()
          ]).then(() => {
            // После первой загрузки данных, пробуем повторно обновить плейлисты и избранное через 10-15 сек (после фоновой синхронизации)
            setTimeout(() => {
              this.fetchPlaylists();
              this.fetchFavoritesFull();
            }, 30000);
          });
        }, 0);
        return { ok: true };
      } catch (e) {
        this.loginStage = '';
        let msg = 'Unknown error';
        if (e?.response?.data?.detail) msg = e.response.data.detail;
        else if (e?.response?.data) msg = JSON.stringify(e.response.data);
        else if (e?.message) msg = e.message;
        return { ok: false, error: msg };
      }
    },
    async register(email, password) {
      this.loginStage = 'Sending requests...';
      try {
        const res = await axios.post('/auth/register', { email, password }, { withCredentials: true });
        this.loginStage = '';
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
        this.saveSession();
        setTimeout(() => { this.loginStage = ''; }, 100);
        setTimeout(() => {
          Promise.allSettled([
            this.fetchConnectedServices(),
            this.fetchPlaylists(),
            this.fetchFavoritesFull(),
            this.fetchFavoritesPlaylistId()
          ]);
        }, 0);
        return { ok: true };
      } catch (e) {
        this.loginStage = '';
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
      this.playlists = {};
      this.favorites = {};
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
    async fetchPlaylists(platform = 'spotify') {
      if (!this.currentUser || !this.currentUser.id) {
        this.error = 'User not logged in or user_id missing';
        return;
      }
      // Получаем плейлисты только один раз за сессию
      if (this.playlists && this.playlists[platform] && this.playlists[platform].length > 0) {
        console.log(`[fetchPlaylists] Playlists for ${platform} already loaded, skip request`);
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        console.log(`[fetchPlaylists] Запрос плейлистов для ${platform}...`);
        // Ожидаем, что каждый плейлист содержит tracks_number
        const res = await axios.get('/playlists', { params: { user_id: this.currentUser.id, platform }, withCredentials: true });
        const basePlaylists = res.data.playlists || [];
        // Проверяем, что у каждого плейлиста есть tracks_number
        basePlaylists.forEach(pl => {
          if (typeof pl.tracks_number === 'undefined') {
            console.warn(`[fetchPlaylists] Плейлист ${pl.title} не содержит tracks_number!`);
          }
        });
        if (!this.playlists) this.playlists = {};
        this.playlists[platform] = basePlaylists;
        console.log(`[fetchPlaylists] Получено плейлистов для ${platform}:`, basePlaylists.length, basePlaylists.map(p => p.id));
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load playlists for ${platform}`;
        console.error(`[fetchPlaylists] Error for ${platform}:`, e);
      } finally {
        this.loading = false;
      }
    },
    async fetchPlaylistTracks(playlistId, platform = 'spotify') {
      if (!playlistId) return;
      // Не трогаем массив плейлистов, только подгружаем треки для выбранного плейлиста
      const pl = this.playlists && this.playlists[platform] && this.playlists[platform].find(p => String(p.id) === String(playlistId));
      if (pl && pl.tracks && pl.tracks.length > 0) return;
      try {
        const res = await axios.get(`/playlists/${playlistId}/tracks`, { params: { platform }, withCredentials: true });
        if (this.playlists && this.playlists[platform]) {
          this.playlists[platform] = this.playlists[platform].map(pl =>
            String(pl.id) === String(playlistId)
              ? { ...pl, tracks: res.data.tracks || [] }
              : pl
          );
        }
      } catch (e) {
        console.error(`[fetchPlaylistTracks] Error for ${platform}:`, e);
        throw e;
      }
    },
    // Ленивая подгрузка избранных треков
    async fetchFavoritesLazy(offset = 0, limit = 50, platform = 'spotify') {
      if (!this.currentUser || !this.currentUser.id) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id, offset, limit, platform }, withCredentials: true });
        if (!this.favorites) this.favorites = {};
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
    async fetchFavoritesFull(platform = 'spotify') {
      if (!this.currentUser || !this.currentUser.id) return;
      if (this.favorites && this.favorites[platform] && this.favorites[platform].length > 0) {
        console.log(`[fetchFavoritesFull] Favorites for ${platform} already loaded, skip request`);
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        console.log(`[fetchFavoritesFull] Запрос избранных треков для ${platform}...`);
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id, platform }, withCredentials: true });
        if (!this.favorites) this.favorites = {};
        this.favorites[platform] = res.data.tracks || [];
        this.favoritesTotal = res.data.tracks_count || (this.favorites[platform] ? this.favorites[platform].length : 0);
        console.log(`[fetchFavoritesFull] Получено избранных для ${platform}:`, this.favorites[platform].length);
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || `Failed to load favorites for ${platform}`;
        console.error(`[fetchFavoritesFull] Ошибка для ${platform}:`, e);
      } finally {
        this.loading = false;
      }
    },
    async fetchFavoritesPlaylistId(platform = 'spotify') {
      if (!this.currentUser || !this.currentUser.id) return;
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id, platform }, withCredentials: true });
        const externalId = res.data?.playlist?.external_id;
        // console.log('[user.js] external_id избранного плейлиста из user_favorites:', externalId);
        if (!externalId) return;
        this.favoritesPlaylistExternalId = externalId;
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
