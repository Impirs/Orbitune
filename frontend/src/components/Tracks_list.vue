<template>
  <div class="tracks-list">
    <div v-if="loading" class="tracks-loader">Loading tracks...</div>
    <div v-else>
      <div v-for="(track, idx) in tracks" :key="track.id || idx" class="track-row" :class="{selected: idx === selectedIdx}" @click="selectTrack(idx)">
        <div class="track-num">{{ idx + 1 }}</div>
        <img :src="track.image_url" class="track-cover" />
        <div class="track-info">
          <div class="track-title">{{ track.title }}</div>
          <div class="track-meta">
            <span class="track-artist">{{ track.artist }}</span>
            <span class="track-album">{{ track.album }}</span>
          </div>
        </div>
        <div class="track-length">{{ formatDuration(track.duration) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();
const props = defineProps({
  playlistId: Number,
});
const tracks = ref([]);
const loading = ref(false);
const selectedIdx = ref(0);

function formatDuration(sec) {
  if (!sec) return '';
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function selectTrack(idx) {
  selectedIdx.value = idx;
}

async function loadTracks() {
  loading.value = true;
  try {
    await userStore.fetchPlaylistTracks(props.playlistId, 'spotify');
    const pl = (userStore.playlists['spotify'] || []).find(p => p.id === props.playlistId);
    if (pl && pl.tracks) {
      tracks.value = pl.tracks
    }
  } finally {
    loading.value = false;
  }
}

watch(() => props.playlistId, () => {
  tracks.value = [];
  loadTracks();
}, { immediate: true });

onMounted(() => {
  loadTracks();
});
</script>

<style scoped>
.tracks-list {
  padding: 18px 16px 18px 0;
  min-width: 0;
  width: 100%;
  min-height: 420px;
  max-height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.tracks-loader {
  color: #bbb;
  text-align: center;
  margin: 24px 0;
}
.track-row {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 12px 32px 12px 16px;
  border-radius: 14px;
  cursor: pointer;
  background: none;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s;
}
.track-row.selected, .track-row:hover {
  background: rgba(255,255,255,0.18);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.08);
}
.track-row:hover {
    transform: translateX(8px);
}
.track-num {
  width: 32px;
  text-align: right;
  color: #bbb;
  font-size: 1.1em;
}
.track-cover {
  width: 54px;
  height: 54px;
  border-radius: 6px;
  object-fit: cover;
  background: #222;
}
.track-info {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-width: 0;
}
.track-title {
  font-size: 1.1em;
  font-weight: 500;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.track-meta {
  font-size: 0.98em;
  color: #bbb;
  display: flex;
  gap: 12px;
}
.track-length {
  width: 54px;
  text-align: right;
  color: #bbb;
  font-size: 1.1em;
}
</style>
