<template>
  <div class="content-platforms">
    <div class="platforms-list">
      <h2>Connected Services</h2>
      <div v-if="userStore.loading" class="loader">Loading services...</div>
      <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
      <template v-else>
        <div v-for="service in connected" :key="service.platform" class="platform-block" @click="select(service)">
          <div class="platform-title">{{ service.platform }}</div>
          <div class="platform-user">{{ service.external_user_id || '—' }}</div>
        </div>
      </template>
    </div>
    <div class="platform-info" v-if="selected">
      <h3>{{ selected.platform }}</h3>
      <div><b>User:</b> {{ selected.external_user_id }}</div>
      <div><b>Subscription:</b> {{ selected.subscription_type || '—' }}</div>
      <div><b>Expires:</b> {{ selected.expires_at || '—' }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();
const connected = computed(() => userStore.connectedServices || []);
const selected = ref(null);
function select(service) {
  selected.value = service;
}
</script>

<style scoped>
.content-platforms {
  display: flex;
  flex-direction: row;
  gap: 40px;
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
.platforms-list {
  min-width: 220px;
  max-width: 260px;
}
.platform-block {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 14px;
  padding: 16px 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  cursor: pointer;
  transition: background 0.15s;
}
.platform-block:hover {
  background: #ffeaea;
}
.platform-title {
  font-weight: bold;
  font-size: 1.1em;
}
.platform-user {
  color: #888;
  font-size: 0.95em;
}
.platform-info {
  background: #fff;
  border-radius: 12px;
  padding: 24px 32px;
  min-width: 320px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
