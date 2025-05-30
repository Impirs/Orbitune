<template>
  <div class="data-manager">
    <img :src="iconUrl" class="dm-icon" />
    <section>
      <div class="dm-data">
        <div class="dm-header">
          <span class="dm-title">{{ serviceName }} Data</span>
        </div>
        <div class="dm-info">
          <span class="dm-playlists">Playlists in Orbitune: <b>{{ playlistsCount }}</b></span>
        </div>
      </div>
      <div class="dm-controller">
        <div class="dm-actions">
          <button class="dm-btn" @click="toggleAutoupdate">
            Autoupdate
            <div class="autoupdate-indicator" :class="{'off': !autoupdateEnabled}" />
          </button>
          <button class="dm-btn" :disabled="loading" @click="syncData">
            <template v-if="loading">
              <img src="https://img.icons8.com/?size=100&id=8zSWPHqkpHQ5&format=png&color=ffffff" class="dm-loader" />
              synchronization
            </template>
            <template v-else>
              Force Update
            </template>
          </button>
        </div>
        <div class="dm-actions">
          <button v-if="service==='youtube'" class="dm-btn import-btn" @click="goToImport">
            Import
          </button>
          <span v-else class="import-placeholder"></span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useUserStore } from '../stores/user';
import { useServicesStore } from '../stores/services';
import { useRouter } from 'vue-router';
const props = defineProps({
  service: { type: String, required: true }
});
const userStore = useUserStore();
const servicesStore = useServicesStore();
const router = useRouter();
const loading = ref(false);
const playlistsCount = ref('…');

const serviceName = computed(() => {
  switch (props.service) {
    case 'spotify': return 'Spotify';
    case 'youtube': return 'YouTube';
    default: return props.service;
  }
});
const iconUrl = computed(() => {
  switch (props.service) {
    case 'spotify': return new URL('../assets/icons/spotify.png', import.meta.url).href;
    case 'youtube': return new URL('../assets/icons/youtube.png', import.meta.url).href;
    default: return '';
  }
});

const autoupdateEnabled = computed(() => getSyncState());

// Получаем sync из connectedServices
function getSyncState() {
  const service = userStore.connectedServices.find(s => s.platform === props.service);
  return service ? service.sync !== false : true;
}

onMounted(async () => {
  if (!userStore.currentUser) return;
  const userId = userStore.currentUser.id;
  try {
    await servicesStore.fetchPlaylists(userId, props.service);
    const pls = servicesStore.playlists[props.service] || [];
    let filtered = pls;
    if (props.service === 'spotify') {
      filtered = pls.filter(pl => (pl.external_id !== 'liked' && pl.title?.toLowerCase() !== 'liked songs'));
    } else if (props.service === 'yandex') {
      filtered = pls.filter(pl => pl.title?.toLowerCase() !== 'моя музыка');
    } else if (props.service === 'youtube') {
      filtered = pls.filter(pl => pl.title?.toLowerCase() !== 'liked songs' && pl.title?.toLowerCase() !== 'понравившиеся');
    }
    playlistsCount.value = filtered.length;
  } catch (e) {
    playlistsCount.value = '?';
  }
});

watch(() => userStore.connectedServices, () => {
  // autoupdateEnabled теперь computed, не нужно обновлять вручную
});

async function toggleAutoupdate() {
  if (!userStore.currentUser) return;
  const userId = userStore.currentUser.id;
  const newSync = !autoupdateEnabled.value;
  try {
    await fetch(`/connected_services/set_sync?user_id=${userId}&platform=${props.service}&sync=${newSync}`, {
      method: 'POST'
    });
    await userStore.fetchConnectedServices(true);
    // autoupdateEnabled теперь computed, не меняем вручную
  } catch (e) {
    // handle error
  }
}

async function syncData() {
  loading.value = true;
  try {
    if (!userStore.currentUser) return;
    const userId = userStore.currentUser.id;
    await fetch(`/connected_services/sync?user_id=${userId}&platform=${props.service}`, { method: 'POST' });
    await userStore.fetchPlaylists(props.service);
  } finally {
    loading.value = false;
  }
}
function goToImport() {
  const nickname = userStore.currentUser?.nickname || 'user';
  router.push({ path: `/${nickname}/youtube_transfer`, query: { from: 'settings' } });
}
</script>

<style scoped>
.data-manager {
  position: relative;
  border: 2px solid rgba(255,255,255,0.33);
  border-radius: 14px;
  padding: 16px 24px 16px 24px;
  margin-bottom: 18px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
}
.data-manager section {
  display: flex;
  width: calc(100% - 48px - 16px);
  flex-direction: row;
  justify-content: space-between;
}
.dm-data {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.dm-controller {
  display: flex;
  flex-direction: column;
}
.dm-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dm-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #222;
}
.dm-title {
  font-size: 1.4em;
  font-weight: 600;
}
.dm-info {
  font-size: 1.08em;
  color: #bbb;
}
.dm-actions {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}
.dm-btn {
  width: 140px;
  align-items: center;
  justify-content: center;
  margin-top: 0;
  padding: 6px 16px;
  color: #fff;
  font-size: 1.1em;
  background: rgba(255, 255, 255, 0.01);
  border-radius: 10px;
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px) saturate(1);
  border: 1px solid rgba(255,255,255,0.33);
  cursor: pointer;
  transition: background 0.18s;
  display: flex;
  align-items: center;
  gap: 16px;
}
.dm-btn:hover {
  background: rgba(255, 255, 255, 0.18);
}
.dm-btn:disabled {
  background: #444;
  cursor: not-allowed;
}
.autoupdate-indicator {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #1db954;
  transition: background 0.2s;
}
.autoupdate-indicator.off {
  background: #ff4444;
}
.import-btn {
  margin-top: 8px;
}
.dm-loader {
  width: 22px;
  height: 22px;
  margin-right: 6px;
  vertical-align: middle;
}
</style>
