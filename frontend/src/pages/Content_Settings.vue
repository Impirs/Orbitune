<template>
  <div class="content-settings">
    <div class="settings-header">
      <h2>Settings</h2>
    </div>
    <div class="settings-content">
      <div class="settings-section">
        <h3>Services</h3>
        <div class="settings-block">
          <div class="settings-subtitle">Your services</div>
          <div class="services-cards">
            <div v-for="service in userStore.connectedServices" :key="service.platform" class="service-card" :class="service.platform" @mouseenter="hoveredService = service.platform" @mouseleave="hoveredService = null">
              <div class="service-card-inner">
                <div class="service-icon">
                  <img :src="getServiceIcon(service.platform)" :alt="service.platform" />
                </div>
                <div class="service-info">
                  <div class="service-title">{{ getServiceName(service.platform) }}</div>
                  <div class="service-user">{{ service.display_name || service.external_user_id }}</div>
                </div>
              </div>
              <button class="logout-btn" @click="logoutService(service.platform)">Logout</button>
            </div>
            <div class="add-service-card" :class="{ expanded: addServicesOpen }" :style="{ width: addServiceCardWidth }">
              <div class="add-plus" @click.stop="toggleAddServices">
                <img src="https://img.icons8.com/?size=100&id=gWujzKh2tSTZ&format=png&color=ffffff80">
              </div>
              <div v-if="addServicesOpen" class="add-services-list">
                <div v-for="srv in filteredAvailableServices" :key="srv.platform" class="add-service-item" @click.stop="connectService(srv.platform)">
                  <img :src="getServiceIcon(srv.platform)" :alt="srv.name" />
                  <span>{{ srv.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="settings-block">
          <div class="settings-subtitle">Data</div>
          <div class="settings-placeholder">Export, import, clear data (coming soon)</div>
        </div>
        <div class="settings-block">
          <div class="settings-subtitle">Player</div>
          <div class="settings-placeholder">Player settings (coming soon)</div>
        </div>
      </div>
      <div class="settings-section">
        <h3>Account</h3>
        <div class="settings-block">
          <div class="settings-subtitle">Change nickname</div>
          <form class="settings-form" @submit.prevent>
            <input type="text" placeholder="New nickname" disabled />
            <button type="submit" disabled>Change</button>
          </form>
        </div>
        <div class="settings-block">
          <div class="settings-subtitle">Change password</div>
          <form class="settings-form" @submit.prevent>
            <input type="password" placeholder="Current password" disabled />
            <input type="password" placeholder="New password" disabled />
            <button type="submit" disabled>Change</button>
          </form>
        </div>
        <div class="settings-block danger">
          <div class="settings-subtitle">Delete account</div>
          <button class="danger-btn" disabled>Delete my account</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import { useServicesStore } from '../stores/services';
const userStore = useUserStore();
const servicesStore = useServicesStore();
const hoveredService = ref(null);
const addServicesOpen = ref(false);

const availableServices = [
  { platform: 'spotify', name: 'Spotify' },
  { platform: 'deezer', name: 'Deezer' },
  { platform: 'youtube', name: 'Youtube' },
  { platform: 'apple', name: 'Apple' },
  { platform: 'soundcloud', name: 'SoundCloud' },
];

const filteredAvailableServices = computed(() => {
  const connected = userStore.connectedServices.map(s => s.platform);
  return availableServices.filter(srv => !connected.includes(srv.platform));
});

const addServiceCardWidth = computed(() => {
  // 142px (base) + 110px * N + 24px (padding)
  const n = filteredAvailableServices.value.length;
  return addServicesOpen.value
    ? `calc(142px + 110px * ${n} )`
    : '140px';
});

function getServiceIcon(platform) {
  switch (platform) {
    case 'spotify': return new URL('../assets/icons/spotify.png', import.meta.url).href;
    case 'deezer': return new URL('../assets/icons/deezer.png', import.meta.url).href;
    case 'youtube': return new URL('../assets/icons/youtube.png', import.meta.url).href;
    case 'apple': return new URL('../assets/icons/apple.png', import.meta.url).href;
    case 'soundcloud': return new URL('../assets/icons/soundcloud.png', import.meta.url).href;
    default: return '';
  }
}
function getServiceName(platform) {
  switch (platform) {
    case 'spotify': return 'Spotify';
    case 'deezer': return 'Deezer';
    case 'youtube': return 'Youtube';
    case 'apple': return 'Apple';
    case 'soundcloud': return 'SoundCloud';
    default: return platform;
  }
}
function toggleAddServices() {
  addServicesOpen.value = !addServicesOpen.value;
}
function connectService(platform) {
  if (platform === 'spotify') {
    window.location.href = '/oauth/spotify/login';
  } else if (platform === 'youtube') {
    window.location.href = '/oauth/google/login';
  } else {
    alert('Coming soon: ' + getServiceName(platform));
  }
}
async function logoutService(platform) {
  if (!userStore.currentUser) return;
  await servicesStore.disconnectService(userStore.currentUser.id, platform);
  await userStore.fetchConnectedServices(true); // Принудительно обновляем
}

onMounted(() => {
  // Гарантируем, что сервисы всегда актуальны при открытии настроек
  userStore.fetchConnectedServices();
});

watch(
  () => userStore.connectedServices,
  () => {
    // filteredAvailableServices и addServiceCardWidth пересчитаются автоматически
    // services-cards обновится реактивно
  },
  { deep: true }
);
</script>

<style scoped>
.content-settings {
  display: flex;
  flex-direction: column;
  position: relative;
  width: calc(100% - 70px);
  height: calc(100% - 64px);
  gap: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px) saturate(2);
  border: 1px solid rgba(255,255,255,0.33);
  min-height: 0;
  min-width: 0;
  padding: 32px 30px 32px 40px;
}
.settings-header h2 {
  font-size: 3em;
  font-weight: 700;
  margin: 0;
  color: #fff;
}
.settings-content {
  height: calc(100% - 42px);
  overflow-y: scroll;
  padding-right: 8px;
}
.settings-section {
  margin-bottom: 36px;
}
.settings-section h3 {
  font-size: 2em;
  font-weight: 700;
  margin-top: 8px;
  margin-bottom: 18px;
  color: #fff;
}
.settings-block {
  margin-bottom: 18px;
  background: rgba(255,255,255,0.08);
  border-radius: 12px;
  padding: 18px 24px 14px 24px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
}
.settings-block.danger {
  background: rgba(255,68,68,0.10);
  border: 1px solid #ff4444;
}
.settings-subtitle {
  font-size: 1.5em;
  font-weight: 600;
  margin-bottom: 10px;
  color: #fff;
}
.settings-form {
  display: flex;
  gap: 12px;
  align-items: center;
}
.settings-form input {
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid #bbb;
  background: #181818;
  color: #fff;
  font-size: 1.1em;
}
.settings-form button {
  padding: 8px 18px;
  border-radius: 8px;
  border: none;
  background: #1db954;
  color: #fff;
  font-weight: bold;
  cursor: not-allowed;
  opacity: 0.7;
}
.danger-btn {
  background: #ff4444;
  color: #fff;
  font-weight: bold;
  border: none;
  border-radius: 8px;
  padding: 8px 18px;
  cursor: not-allowed;
  opacity: 0.7;
}
/* --------------- Services --------------- */
/* ---------- Services cards ---------- */
.services-cards {
  display: flex;
  /* position: relative; */
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 8px;
  gap: 12px;
  align-items: center;
}
.service-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  border: 1px solid rgba(255,255,255,0.33);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.24);
  position: relative;
  transition: background 0.3s, box-shadow 0.3s, transform 0.3s, width 0.3s, height 0.3s;
  cursor: default;
  overflow: hidden;
}
.service-card-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  transition: height 0.22s cubic-bezier(0.4,0,0.2,1);
}
.service-card:hover .service-card-inner {
  height: 60%;
}
.service-icon {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 18px;
  margin-bottom: 8px;
}
.service-icon img {
  width: 54px;
  height: 54px;
  object-fit: contain;
}
.service-info {
  text-align: center;
  margin-bottom: 12px;
  opacity: 1;
  transition: opacity 0.18s cubic-bezier(0.4,0,0.2,1), visibility 0.18s cubic-bezier(0.4,0,0.2,1);
}
.service-card:hover .service-info {
  opacity: 0;
  visibility: hidden;
}
.logout-btn {
  position: absolute;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%) translateY(20px);
  padding: 10px 32px;
  border-radius: 20px;
  border: 1px solid #ff4444;
  background: rgba(255,68,68,0.40);
  color: #fff;
  font-weight: bold;
  font-size: 1.1em;
  cursor: pointer;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.25s, transform 0.25s;
  z-index: 2;
}
.service-card:hover .logout-btn {
  opacity: 1;
  pointer-events: auto;
  transform: translateX(-50%) translateY(0);
}
/* ---------- Add services ---------- */
.add-service-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  position: relative;
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  height: 140px;
  border-radius: 28px;
  border: 1px solid rgba(255,255,255,0.33);
  transition: background 0.3s, width 0.35s cubic-bezier(0.4,0,0.2,1);
  overflow: hidden;
  padding-left: 0;
  padding-right: 0;
}
.add-plus {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-left: calc((140px - 64px )/ 2);
  padding-right: 12px;
  height: 140px;
  user-select: none;
  margin-right: 0;
  z-index: 2;
  cursor: pointer;
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
}
.add-plus img {
  width: 64px;
  height: 64px;
  transition: transform 0.35s cubic-bezier(0.4,0,0.2,1);
}
.add-service-card .add-plus {
  /* Center + vertically and horizontally in collapsed state */
  justify-content: center;
  align-items: center;
}
.add-service-card.expanded .add-plus img {
  transform: rotate(90deg);
}
.add-service-card:not(.expanded) .add-plus img {
  transform: rotate(0deg);
}
.add-services-list {
  display: flex;
  flex-direction: row;
  align-items: center;
  width: auto;
  height: 100%;
  justify-content: flex-start;
}
.add-service-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border: 1px solid transparent;
  border-radius: 8px;
  gap: 6px;
  height: 96px;
  width: 108px;
  color: #fff;
  cursor: pointer;
  transition: color 0.2s;
}
.add-service-item img {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #222;
  margin-bottom: 4px;
}
.add-service-item span {
  font-size: 1.4em;
  color: #fff;
  font-weight: 500;
}
.add-service-item:hover {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
}
.logout-fade-enter-active, .logout-fade-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}
.logout-fade-enter-from, .logout-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
/* ---------- Services DATA ---------- */
.settings-placeholder {
  color: #bbb;
  font-size: 1.05em;
  padding: 6px 0 2px 0;
}
</style>
