<template>
  <nav class="navbar">
    <div class="navbar-left">
      <router-link to="/" class="icon-btn">
        <div class="icon-placeholder"></div>
      </router-link>
    </div>
    <div class="navbar-right">
      <template v-if="!userStore.isLoggedIn">
        <router-link to="/auth?mode=login" class="nav-btn">Login</router-link>
        <router-link to="/auth?mode=register" class="nav-btn">Register</router-link>
      </template>
      <template v-else>
        <input class="search-input" placeholder="Search..." />
        <div class="user-placeholder">
          <span class="user-name">{{ userStore.currentUser?.nickname || userStore.currentUser?.name }}</span>
          <div class="user-icon"></div>
        </div>
        <button @click="logout" class="exit-btn">
          <div class="icon-placeholder"></div>
        </button>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

function logout() {
  userStore.logout();
  router.push('/');
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  height: 63px;
  background: #090b17;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border-bottom: 1px solid #162036bf;
  z-index: 100;
  padding: 0 40px;
}
.navbar-left {
  display: flex;
  align-items: center;
}
.icon-btn {
  display: flex;
  align-items: center;
}
.icon-placeholder {
  width: 48px;
  height: 48px;
  background: #ff4444;
  border-radius: 8px;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.nav-btn {
  color: #ff4444;
  font-weight: bold;
  text-decoration: none;
  margin-left: 16px;
}
.search-input {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #eee;
  font-size: 1em;
}
.user-placeholder {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: fit-content;
}
.user-name {
  color: #fff;
  margin-left: 16px;
  font-weight: bold;
}
.user-icon {
  width: 32px;
  height: 32px;
  background: #ff4444;
  border-radius: 50%;
  margin-left: 12px;
}

.exit-btn {
  background: none;
  border: none;
  margin-left: 12px;
  cursor: pointer;
}
.exit-btn .icon-placeholder {
  width: 32px;
  height: 32px;
  background: #ff4444;
  border-radius: 6px;
}
</style>