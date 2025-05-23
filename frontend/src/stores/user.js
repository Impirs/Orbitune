import { defineStore } from 'pinia';
import axios from 'axios';
import { useServicesStore } from './services';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false,
    connectedServices: [],
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
        setTimeout(() => { this.loginStage = ''; }, 100);
        setTimeout(() => {
          Promise.allSettled([
            this.fetchConnectedServices()
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
            this.fetchConnectedServices()
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
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
      axios.post('/auth/logout', {}, { withCredentials: true });
    },
    async fetchConnectedServices(force = false) {
      if (!this.currentUser) return;
      if (!force && this.connectedServices && this.connectedServices.length > 0) {
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
        const promises = [];
        if (!this.connectedServices || this.connectedServices.length === 0) {
          promises.push(this.fetchConnectedServices());
        }
        await Promise.all(promises);
        this.loading = false;
        console.log('[initialize] Основные данные пользователя загружены');
      }
    },
    saveSession() {
      localStorage.setItem('currentUser', JSON.stringify(this.currentUser));
      localStorage.setItem('isLoggedIn', 'true');
    }
  }
});
