<template>
  <div class="youtube-transfer">
    <h2>Select playlists to import from YouTube Music</h2>
    <div v-if="loading" class="loader">Loading playlists...</div>
    <div v-else-if="error" class="error-block">{{ error }}</div>
    <div v-else>
      <div class="playlist-list">
        <div v-for="pl in playlists" :key="pl.id" class="playlist-row">
          <input type="checkbox" v-model="selected" :value="pl.id" />
          <img :src="pl.cover_url || fallbackCover" class="playlist-cover" />
          <div class="playlist-info">
            <div class="playlist-title">{{ pl.title }}</div>
            <div class="playlist-count">{{ pl.tracks_count }} tracks</div>
          </div>
        </div>
      </div>
      <button class="import-btn" :disabled="selected.length === 0 || importing" @click="importSelected">Import Selected</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
const playlists = ref([]);
const selected = ref([]);
const loading = ref(true);
const error = ref('');
const importing = ref(false);
const fallbackCover = new URL('../../assets/music_universe.png', import.meta.url).href;

onMounted(async () => {
  loading.value = true;
  error.value = '';
  try {
    // эндпоинт: /youtube/fetch_temp_data
    const user = JSON.parse(localStorage.getItem('currentUser'));
    const userId = user?.id;
    if (!userId) throw new Error('User not found');
    const res = await axios.get(`/youtube/fetch_temp_data?user_id=${userId}`, { withCredentials: true });
    console.log('Raw response:', res); 
    console.log('Fetched playlists:', res.data);
    playlists.value = res.data.playlists || [];
    console.log('Parsed playlists.value:', playlists.value);
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load playlists';
    console.error('Error loading playlists:', e);
  } finally {
    loading.value = false;
  }
});

async function importSelected() {
  if (!selected.value.length) return;
  importing.value = true;
  try {
    // только выбранные плейлисты 
    const user = JSON.parse(localStorage.getItem('currentUser'));
    const userId = user?.id;
    if (!userId) throw new Error('User not found');
    const selectedPlaylists = playlists.value.filter(pl => selected.value.includes(pl.id));
    await axios.post('/youtube/import_playlists', { user_id: userId, playlists: selectedPlaylists }, { withCredentials: true });
    window.location.href = `/${user?.nickname || 'user'}/home`;
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Import failed';
  } finally {
    importing.value = false;
  }
}
</script>

<style scoped>
.youtube-transfer {
  max-width: 600px;
  margin: 40px auto;
  background: #181c2a;
  border-radius: 18px;
  padding: 32px 32px 24px 32px;
  color: #fff;
  box-shadow: 0 2px 32px 0 rgba(0,0,0,0.18);
}
.playlist-list {
  margin: 24px 0 18px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.playlist-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.06);
  border-radius: 10px;
  padding: 8px 12px;
}
.playlist-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  background: #222;
}
.playlist-info {
  flex: 1;
}
.playlist-title {
  font-size: 1.1em;
  font-weight: 600;
}
.playlist-count {
  font-size: 0.98em;
  color: #bbb;
}
.import-btn {
  margin-top: 18px;
  padding: 10px 32px;
  border-radius: 12px;
  background: #1db954;
  color: #fff;
  font-weight: bold;
  border: none;
  font-size: 1.1em;
  cursor: pointer;
  transition: background 0.18s;
}
.import-btn:disabled {
  background: #444;
  cursor: not-allowed;
}
.loader, .error-block {
  margin: 32px 0;
  text-align: center;
  color: #bbb;
}
.error-block {
  color: #ff4444;
}
</style>
