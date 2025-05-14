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
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/connected_services', { params: { user_id: this.currentUser.id }, withCredentials: true });
        this.connectedServices = res.data;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load services';
      } finally {
        this.loading = false;
      }
    },
    async fetchPlaylists() {
      if (!this.currentUser || !this.currentUser.id) {
        this.error = 'User not logged in or user_id missing';
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        // Быстрая загрузка только списка плейлистов
        const res = await axios.get('/playlists', { params: { user_id: this.currentUser.id }, withCredentials: true });
        const basePlaylists = res.data.playlists || [];
        // Сразу отображаем список без треков и количества
        this.playlists = { spotify: basePlaylists };
        // Асинхронно подгружаем количество треков и треки для каждого плейлиста
        basePlaylists.forEach(async (pl, idx) => {
          try {
            const tracksRes = await axios.get(`/playlists/${pl.id}/tracks`, { withCredentials: true });
            // Обновляем только нужный плейлист
            if (this.playlists.spotify[idx] && tracksRes.data) {
              this.playlists.spotify[idx] = {
                ...this.playlists.spotify[idx],
                tracks: tracksRes.data.tracks,
                tracks_count: tracksRes.data.tracks_count
              };
            }
          } catch (e) {
            // Не блокируем загрузку, просто не обновляем треки
          }
        });
        await this.fetchFavorites();
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load playlists';
        console.error('[fetchPlaylists] Error:', e);
      } finally {
        this.loading = false;
      }
    },
    async fetchFavorites() {
      if (!this.currentUser || !this.currentUser.id) {
        this.error = 'User not logged in or user_id missing';
        return;
      }
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id }, withCredentials: true });
        this.favorites = res.data.tracks || [];
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load favorites';
        console.error('[fetchFavorites] Error:', e);
      } finally {
        this.loading = false;
      }
    },
    initialize() {
      const user = localStorage.getItem('currentUser');
      const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
      if (user && loggedIn) {
        try {
          this.currentUser = JSON.parse(user);
        } catch {
          this.currentUser = null;
        }
        this.isLoggedIn = true;
      }
    },
    saveSession() {
      localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
      localStorage.setItem('isLoggedIn', 'true');
    },
  },
});
