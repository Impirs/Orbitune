<template>
  <div class="content-settings">
    <h2>Settings</h2>
    <p>Manage your connected services:</p>
    <div v-if="userStore.loading" class="loader">Loading services...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <div class="services-list" v-else>
      <div v-for="service in userStore.connectedServices" :key="service.platform" class="service-item">
        <span class="service-name">{{ service.platform }}</span>
        <button v-if="!service.is_connected" @click="connect(service.platform)">Connect</button>
        <button v-else @click="disconnect(service.platform)">Disconnect</button>
      </div>
    </div>
    <div class="oauth-auth-block">
      <h3>Authorize new service</h3>
      <button class="oauth-btn google" @click="connect('google')">Connect Google</button>
      <button class="oauth-btn spotify" @click="connect('spotify')">Connect Spotify</button>
      <button class="oauth-btn yandex" @click="connect('yandex')">Connect Yandex</button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();

onMounted(() => {
  userStore.fetchConnectedServices();
});

function connect(platform) {
  if (platform === 'google') {
    window.location.href = '/oauth/google/login';
  } else if (platform === 'spotify') {
    window.location.href = '/oauth/spotify/login';
  } else if (platform === 'yandex') {
    window.location.href = '/oauth/yandex/login';
  }
}
function disconnect(platform) {
  // TODO: реализовать запрос на отключение сервиса
  alert('Disconnect ' + platform + ' (реализовать на бэке)');
}
</script>

<style scoped>
.content-settings {
  padding: 32px;
}
.loader {
  color: #888;
  margin: 24px 0;
}
.error-block {
  color: #ff4444;
  margin: 24px 0;
  font-weight: bold;
}
.services-list {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.service-item {
  display: flex;
  align-items: center;
  gap: 16px;
}
.service-name {
  font-weight: bold;
  text-transform: capitalize;
}
button {
  padding: 6px 18px;
  border-radius: 8px;
  border: none;
  background: #ff4444;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
}
.oauth-auth-block {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.oauth-btn.google {
  background: #fff;
  color: #222;
  border: 1px solid #eee;
}
.oauth-btn.spotify {
  background: #1db954;
  color: #fff;
}
.oauth-btn.yandex {
  background: #f2412e;
  color: #222;
  border: 1px solid #eee;
}
</style>
