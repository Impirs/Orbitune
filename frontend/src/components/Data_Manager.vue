<template>
  <div class="data-manager">
    <div class="dm-header">
      <img :src="iconUrl" class="dm-icon" />
      <span class="dm-title">{{ serviceName }} Data</span>
    </div>
    <div class="dm-info">
      <span class="dm-playlists">Playlists in Orbitune: <b>{{ playlistsCount }}</b></span>
    </div>
    <button class="dm-btn" :disabled="loading" @click="syncData">
      <template v-if="loading">
        <img src="https://img.icons8.com/?size=100&id=8zSWPHqkpHQ5&format=png&color=ffffff" class="dm-loader" />
        synchronization
      </template>
      <template v-else>
        Update data
      </template>
    </button>
    <button v-if="service==='youtube'" class="dm-btn import-btn" @click="goToImport">
      Import
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
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

onMounted(async () => {
  if (!userStore.currentUser) return;
  const userId = userStore.currentUser.id;
  try {
    await servicesStore.fetchPlaylists(userId, props.service);
    const pls = servicesStore.playlists[props.service] || [];
    // Фильтрация спецплейлистов (например, Liked Songs) — как раньше
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

async function syncData() {
  loading.value = true;
  try {
    await userStore.syncPlatform(props.service);
    await userStore.fetchPlaylists(props.service);
  } finally {
    loading.value = false;
  }
}
function goToImport() {
  const nickname = userStore.currentUser?.nickname || 'user';
  router.push(`/${nickname}/youtube_transfer`);
}
</script>

<style scoped>
.data-manager {
  background: rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 18px 24px 18px 24px;
  margin-bottom: 18px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}
.dm-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.dm-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #222;
}
.dm-title {
  font-size: 1.2em;
  font-weight: 600;
}
.dm-info {
  font-size: 1.08em;
  color: #bbb;
}
.dm-btn {
  margin-top: 4px;
  padding: 8px 22px;
  border-radius: 10px;
  background: #1db954;
  color: #fff;
  font-weight: bold;
  border: none;
  font-size: 1.08em;
  cursor: pointer;
  transition: background 0.18s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.dm-btn:disabled {
  background: #444;
  cursor: not-allowed;
}
.import-btn {
  background: #1a73e8;
  margin-left: 8px;
}
.dm-loader {
  width: 22px;
  height: 22px;
  margin-right: 6px;
  vertical-align: middle;
}
</style>
