<template>
  <div class="tracks-container">
    <div class="list-header">
      <div class="playlist-title-row">
        <span>{{ playlistTitle }}</span>
      </div>
      <div class="columns-row">
        <div class="track-num-col">#</div>
        <div class="track-title-col">Title</div>
        <div class="track-album-col">Album</div>
        <div class="track-length-col">Time</div>
      </div>
    </div>
    <div class="tracks-list">
      <div v-if="loading" class="tracks-loader">Loading tracks...</div>
      <div v-else>
        <div v-for="(track, idx) in tracks" :key="track.id || idx" class="track-row" :class="{selected: idx === selectedIdx}" @click="selectTrack(idx)">
          <div class="track-num-col track-num">{{ idx + 1 }}</div>
          <div class="track-title-col track-title">
            <div class="track-title-main">{{ formatTitle(track.title) }}</div>
            <div class="track-artist">{{ formatArtists(track.artist) }}</div>
          </div>
          <div class="track-album-col track-album">{{ formatAlbum(track.album) }}</div>
          <div class="track-length-col track-length">{{ formatDuration(track.duration) }}</div>
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
const props = defineProps({
  playlistId: Number,
  platform: { type: String, required: true }
});
const tracks = ref([]);
const loading = ref(false);
const selectedIdx = ref(null);

const playlists = computed(() => servicesStore.playlists[props.platform] || []);
const playlist = computed(() => playlists.value.find(p => p.id === props.playlistId));
const playlistTitle = computed(() => playlist.value ? playlist.value.title : '');

function formatDuration(sec) {
  if (!sec) return '';
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatArtists(artistStr) {
  if (!artistStr) return '';
  const arr = artistStr.split(',').map(a => a.trim());
  if (arr.length <= 3) return arr.join(', ');
  return arr.slice(0, 3).join(', ') + ', …';
}

function formatTitle(title) {
  if (!title) return '';
  return title
    .replace(/\s*[\[(][^\])\]]*[\])]/g, '') 
    .replace(/"[^"]*"/g, '')
    .trim();
}

function formatAlbum(album) {
  if (!album) return '';
  return album.replace(/\s*[\[(][^\])\]]*[\])]/g, '').trim();
}

function selectTrack(idx) {
  selectedIdx.value = idx;
}

async function loadTracks() {
  loading.value = true;
  try {
    await servicesStore.fetchPlaylistTracks(userStore.currentUser?.id, props.playlistId, props.platform);
    const pl = (servicesStore.playlists[props.platform] || []).find(p => p.id === props.playlistId);
    if (pl && pl.tracks) {
      tracks.value = pl.tracks;
    }
  } finally {
    loading.value = false;
  }
}

watch([() => props.playlistId, playlists], ([pid, pls]) => {
  if (pid) {
    tracks.value = [];
    loadTracks();
  }
}, { immediate: true });

onMounted(() => {
  if (props.playlistId) {
    loadTracks();
  }
});
</script>

<style scoped>
.tracks-container {
  display: flex;
  flex-direction: column;
  /* width: 100%; */
  min-width: 0;
  max-width: 100%;
  padding: 18px 16px 18px 0;
  background: transparent;
}
.list-header {
  padding: 0 46px 3px 0;
  background: transparent;
  display: flex;
  flex-direction: column;
}
.playlist-title-row {
  display: flex;
  height: 32px;
  align-items: center;
  padding-left: 54px;
}
.playlist-title-row span {
  height: 25px;
  font-size: 1.8em;
  font-weight: 600;
  color: #fff;
}
.columns-row {
  display: grid;
  grid-template-columns: 1fr 9fr 9fr 3fr;
  align-items: center;
  font-size: 1em;
  color: #bbb;
  font-weight: 500;
  gap: 0;
}
.track-row {
  display: grid;
  grid-template-columns: 1fr 9fr 9fr 3fr;
  align-items: center;
  gap: 0;
  width: calc(100% - 32px);
  padding: 12px 24px 12px 0;
  border-radius: 14px;
  cursor: pointer;
  background: none;
  transition: background 0.1s, box-shadow 0.1s, transform 0.1s;
}
.track-num-col {
  text-align: right;
}
.track-title-col {
  min-width: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.track-album-col {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.track-length-col {
  text-align: right;
}
@media (max-width: 900px) {
  .columns-row, .track-row {
    grid-template-columns: 1fr 9fr 9fr 3fr;
  }
  .track-album-col {
    display: none !important;
  }
}
@media (max-width: 640px) {
  .columns-row, .track-row {
    grid-template-columns: 1fr 7fr 3fr;
  }
  .track-album-col { display: none !important; }
}
.tracks-list {
  min-width: 0;
  width: 100%;
  min-height: 420px;
  max-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.tracks-loader {
  color: #bbb;
  text-align: center;
  margin: 24px 0;
}
.track-row.selected, .track-row:hover {
  background: rgba(255,255,255,0.18);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.08);
}
.track-row:hover {
    transform: translateX(8px);
}
.track-title, .track-title-col {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  flex-direction: column;
}
.track-title-main {
  font-weight: 500;
  color: #fff;
  font-size: 1.1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.track-artist {
  font-size: 0.98em;
  color: #bbb;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.track-album, .track-album-col {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
