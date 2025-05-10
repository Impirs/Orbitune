import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    isLoggedIn: false,
  }),
  actions: {
    login(username, password) {
      if (username === 'admin' && password === 'admin') {
        this.currentUser = 'admin';
        this.isLoggedIn = true;
        localStorage.setItem('currentUser', this.currentUser);
        localStorage.setItem('isLoggedIn', 'true');
        return true;
      }
      return false;
    },
    logout() {
      this.currentUser = null;
      this.isLoggedIn = false;
      localStorage.removeItem('currentUser');
      localStorage.removeItem('isLoggedIn');
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
