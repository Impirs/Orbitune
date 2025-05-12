import { defineStore } from 'pinia';
import axios from 'axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false,
    connectedServices: [],
    playlists: [],
  }),
  actions: {
    async login(email, password) {
      try {
        console.log('[LOGIN] Sending:', { email, password });
        const res = await axios.post('/auth/login', { email, password }, { withCredentials: true });
        console.log('[LOGIN] Response:', res.data);
        this.currentUser = res.data.user;
        this.isLoggedIn = true;
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
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
      axios.post('/auth/logout', {}, { withCredentials: true });
    },
    async fetchConnectedServices() {
      if (!this.currentUser) return;
      const res = await axios.get('/connected_services', { params: { user_id: this.currentUser.id }, withCredentials: true });
      this.connectedServices = res.data;
    },
    async fetchPlaylists() {
      if (!this.currentUser) return;
      const res = await axios.get('/playlists', { params: { user_id: this.currentUser.id }, withCredentials: true });
      this.playlists = res.data;
    },
    initialize() {
      const user = localStorage.getItem('currentUser');
      const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
      if (user && loggedIn) {
        this.currentUser = user;
        this.isLoggedIn = true;
      }
    },
  },
});
