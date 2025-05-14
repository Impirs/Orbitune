<template>
  <div class="content-platforms">
    <div class="platforms-list">
      <h2>Connected Services</h2>
      <div v-if="userStore.loading" class="loader">Loading services...</div>
      <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
      <template v-else>
        <div
          v-for="(service, idx) in connected"
          :key="service.platform"
          class="platform-card"
          :class="service.platform"
          :tabindex="0"
          @click="select(service)"
          :aria-selected="selected?.platform === service.platform"
        >
          <div class="platform-card-content">
            <div class="platform-card-title">{{ getPlatformName(service.platform) }}</div>
            <div class="platform-card-user">{{ service.display_name || service.external_user_id || '—' }}</div>
            <div class="platform-card-subscription">
              <span v-if="service.subscription_expires">Your subscription expires in {{ service.subscription_expires }}</span>
              <span v-else-if="service.subscription_type">{{ service.subscription_type }} subscription</span>
              <span v-else>Subscription info unavailable</span>
            </div>
          </div>
          <div class="platform-card-icon">
            <span class="icon-user"></span>
          </div>
        </div>
        <div class="platform-card add-card" @click="goToSettings">
          <div class="plus">+</div>
        </div>
      </template>
    </div>
    <div class="platform-info" v-if="selected">
      <div class="platform-info-header" :class="selected.platform">
        <div class="platform-info-icon"><span class="icon-user"></span></div>
        <div class="platform-info-title">{{ getPlatformName(selected.platform) }}</div>
        <div class="platform-info-user">{{ selected.display_name || selected.external_user_id }}</div>
      </div>
      <div class="platform-info-details">
        <div><b>Songs</b> <span>{{ selected.songs || '—' }}</span></div>
        <div><b>Playlists</b> <span>{{ selected.playlists || '—' }}</span></div>
        <div><b>Subscription</b> <span>{{ selected.subscription_type || '—' }}</span></div>
        <div><b>Expires</b> <span>{{ selected.subscription_expires || formatDate(selected.expires_at) || '—' }}</span></div>
      </div>
      <div class="platform-actions">
        <button class="action-btn" @click="goToFavorites(selected)">My Favorites</button>
        <button class="action-btn" @click="goToPlaylists(selected)">My Playlists</button>
        <button class="manage-btn" @click="goToSettings">Manage Services</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
const userStore = useUserStore();
const router = useRouter();
const connected = computed(() => userStore.connectedServices || []);
const selected = ref(null);

function getPlatformName(platform) {
  if (platform === 'spotify') return 'Spotify';
  if (platform === 'yandex') return 'Yandex Music';
  if (platform === 'google') return 'YouTube Music';
  return platform.charAt(0).toUpperCase() + platform.slice(1);
}

function formatDate(dateString) {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  } catch (e) {
    return dateString;
  }
}

function select(service) {
  selected.value = service;
}

function goToSettings() {
  // Переход в настройки пользователя
  if (userStore.currentUser && userStore.currentUser.nickname) {
    router.push('/' + userStore.currentUser.nickname + '/home?settings=1');
  } else {
    router.push('/auth');
  }
}

function goToFavorites(service) {
  if (userStore.currentUser && userStore.currentUser.nickname) {
    router.push({
      path: `/${userStore.currentUser.nickname}/home`,
      query: { tab: 'Player', player: 1 }
    });
    userStore.fetchFavorites();
  }
}

function goToPlaylists(service) {
  if (userStore.currentUser && userStore.currentUser.nickname) {
    router.push({
      path: `/${userStore.currentUser.nickname}/home`,
      query: { tab: 'Playlists', service: service.platform }
    });
    userStore.fetchPlaylists();
  }
}

onMounted(() => {
  userStore.fetchConnectedServices();
  if (connected.value.length > 0) {
    selected.value = connected.value[0];
  }
});

watch(connected, (val) => {
  if (val.length > 0 && !selected.value) {
    selected.value = val[0];
  }
});
</script>

<style scoped>
.content-platforms {
  display: flex;
  flex-direction: row;
  gap: 40px;
  padding: 32px;
}
.platforms-list {
  min-width: 320px;
  max-width: 340px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.platform-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 24px;
  padding: 24px 28px;
  margin-bottom: 0;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  transition: background 0.2s, box-shadow 0.2s;
  background: #eee;
  color: #222;
  min-height: 100px;
  position: relative;
}
.platform-card.spotify {
  background: #1db954;
  color: #fff;
}
.platform-card.yandex {
  background: #ff4444;
  color: #fff;
}
.platform-card.google {
  background: #fbbc05;
  color: #222;
}
.platform-card.add-card {
  background: #666;
  color: #fff;
  justify-content: center;
  align-items: center;
  min-height: 80px;
  font-size: 2.5em;
  font-weight: bold;
  cursor: pointer;
  margin-top: 18px;
}
.platform-card-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.platform-card-title {
  font-size: 1.3em;
  font-weight: bold;
}
.platform-card-user {
  font-size: 1.1em;
  font-weight: 500;
}
.platform-card-subscription {
  font-size: 0.98em;
  opacity: 0.9;
}
.platform-card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255,255,255,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
}
.icon-user {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: url('data:image/svg+xml;utf8,<svg fill="%23fff" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="8" r="4"/><path d="M12 14c-4.418 0-8 1.79-8 4v2h16v-2c0-2.21-3.582-4-8-4z"/></svg>') no-repeat center/contain;
}
.plus {
  font-size: 2.5em;
  color: #fff;
  text-align: center;
  width: 100%;
}
.platform-info {
  background: #fff;
  border-radius: 24px;
  padding: 36px 48px;
  min-width: 340px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  max-width: 420px;
}
.platform-info-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
  margin-bottom: 12px;
}
.platform-info-header.spotify {
  color: #1db954;
}
.platform-info-header.yandex {
  color: #ff4444;
}
.platform-info-header.google {
  color: #fbbc05;
}
.platform-info-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255,255,255,0.18);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.platform-info-title {
  font-size: 2em;
  font-weight: bold;
}
.platform-info-user {
  font-size: 1.2em;
  font-weight: 500;
  opacity: 0.8;
}
.platform-info-details {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 1.1em;
}
.platform-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  margin-top: 12px;
}
.action-btn {
  padding: 12px 24px;
  border-radius: 16px;
  border: none;
  background: #f5f5f5;
  color: #333;
  font-size: 1.1em;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}
.action-btn:hover {
  background: #e5e5e5;
}
.manage-btn {
  margin-top: 12px;
  padding: 12px 36px;
  border-radius: 16px;
  border: 2px solid #ff4444;
  background: none;
  color: #ff4444;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.manage-btn:hover {
  background: #ff4444;
  color: #fff;
}
.loader {
  margin: 20px 0;
  font-size: 1.1em;
  color: #777;
}
.error-block {
  margin: 20px 0;
  padding: 16px;
  background: #ffe6e6;
  border-radius: 8px;
  color: #ff4444;
  font-weight: 500;
}
</style>
