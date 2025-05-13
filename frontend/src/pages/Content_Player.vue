<template>
  <div class="content-player">
    <h2>Player</h2>
    <div v-if="userStore.loading" class="loader">Loading tracks...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <div v-else-if="!playlist && !isFavorites">
      <p>Select a playlist to view tracks.</p>
    </div>
    <div v-else>
      <h3 v-if="isFavorites">Favorites</h3>
      <h3 v-else>{{ playlist.title }} <span style="color:#888;font-size:0.9em;">({{ service }})</span></h3>
      <ul>
        <li v-for="track in tracksToShow" :key="track.id || track.title">
          {{ track.title }} — {{ track.artist }}
        </li>
      </ul>
      <div v-if="tracksToShow.length === 0" style="color:#888;">No tracks in playlist.</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();
const route = useRoute();

const service = computed(() => route.query.service || '');
const playlistId = computed(() => route.query.playlistId);
const isFavorites = computed(() => !service.value && !playlistId.value);
const playlist = computed(() => {
  if (!service.value || !playlistId.value) return null;
  const pls = userStore.playlists[service.value] || [];
  return pls.find(pl => String(pl.id) === String(playlistId.value));
});
const tracksToShow = computed(() => {
  if (isFavorites.value) return userStore.favorites || [];
  return playlist.value?.tracks || [];
});
</script>

<style scoped>
.content-player {
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
ul {
  margin-top: 18px;
  padding: 0;
  list-style: none;
}
li {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 8px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
</style>
