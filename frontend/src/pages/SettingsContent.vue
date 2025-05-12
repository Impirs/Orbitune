<template>
  <div class="content-settings">
    <h2>Settings</h2>
    <p>Manage your connected services:</p>
    <div class="services-list">
      <div v-for="service in userStore.connectedServices" :key="service.platform" class="service-item">
        <span class="service-name">{{ service.platform }}</span>
        <button v-if="!service.is_connected" @click="connect(service.platform)">Connect</button>
        <button v-else @click="disconnect(service.platform)">Disconnect</button>
      </div>
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
</style>
