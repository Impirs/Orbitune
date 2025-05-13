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
    async login(email, password) {
      try {
        console.log('[LOGIN] Sending:', { email, password });
        const res = await axios.post('/auth/login', { email, password }, { withCredentials: true });
        console.log('[LOGIN] Response:', res.data);
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
        this.saveSession();
        await this.fetchConnectedServices();
        return { ok: true };
      } catch (e) {
        // Подробный лог для диагностики
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
        // Подробный лог для диагностики
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
      if (!this.currentUser) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/playlists', { params: { user_id: this.currentUser.id }, withCredentials: true });
        if (Array.isArray(res.data)) {
          this.playlists = { orbitune: res.data };
        } else {
          this.playlists = res.data;
        }
        await this.fetchFavorites();
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load playlists';
      } finally {
        this.loading = false;
      }
    },
    async fetchFavorites() {
      if (!this.currentUser) return;
      this.loading = true;
      this.error = '';
      try {
        const res = await axios.get('/favorites', { params: { user_id: this.currentUser.id }, withCredentials: true });
        this.favorites = res.data;
      } catch (e) {
        this.error = e?.response?.data?.detail || e?.message || 'Failed to load favorites';
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
