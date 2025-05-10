<template>
  <nav class="navbar">
    <div class="navbar-left">
      <router-link to="/" class="icon-btn">
        <div class="icon-placeholder"></div>
      </router-link>
    </div>
    <div class="navbar-right">
      <template v-if="!user">
        <router-link to="/login" class="nav-btn">Login</router-link>
        <router-link to="/register" class="nav-btn">Register</router-link>
      </template>
      <template v-else>
        <input class="search-input" placeholder="Поиск..." />
        <span class="user-name">{{ user.name }}</span>
        <div class="user-icon"></div>
        <button class="settings-btn">
          <div class="icon-placeholder"></div>
        </button>
      </template>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  user: Object
})
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  width: calc(100vw - 80px);
  height: 64px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
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
  width: 40px;
  height: 40px;
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
.user-name {
  margin-left: 16px;
  font-weight: bold;
}
.user-icon {
  width: 32px;
  height: 32px;
  background: #ff4444;
  border-radius: 8px;
  margin-left: 12px;
}
.settings-btn {
  background: none;
  border: none;
  margin-left: 12px;
  cursor: pointer;
}
.settings-btn .icon-placeholder {
  width: 28px;
  height: 28px;
  background: #ff4444;
  border-radius: 6px;
}
</style>