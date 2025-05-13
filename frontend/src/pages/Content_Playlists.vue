<template>
  <div class="content-playlists">
    <h2>Playlists</h2>
    <div v-if="userStore.loading" class="loader">Loading playlists...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <template v-else-if="!userStore.playlists || Object.keys(userStore.playlists).length === 0">
      <div>No playlists found.</div>
    </template>
    <template v-else>
      <div v-for="(pls, service) in userStore.playlists" :key="service" class="playlist-service-block">
        <h3>{{ service.charAt(0).toUpperCase() + service.slice(1) }}</h3>
        <ul>
          <li v-for="pl in pls" :key="pl.id" @click="openPlaylist(service, pl)">
            <div class="playlist-title">{{ pl.title }}</div>
            <div class="playlist-platform">Platform: {{ pl.source_platform || service }}</div>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
const userStore = useUserStore();
const router = useRouter();

onMounted(() => {
  userStore.fetchPlaylists();
});

function openPlaylist(service, playlist) {
  // Переход в Player с передачей id плейлиста и сервиса
  router.push({ name: 'UserHome', query: { player: 1, service, playlistId: playlist.id } });
}
</script>

<style scoped>
.content-playlists {
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
.playlist-service-block {
  margin-bottom: 28px;
}
ul {
  margin-top: 8px;
  padding: 0;
  list-style: none;
}
li {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  cursor: pointer;
  transition: background 0.15s;
}
li:hover {
  background: #ffeaea;
}
.playlist-title {
  font-weight: bold;
  font-size: 1.1em;
}
.playlist-platform {
  color: #888;
  font-size: 0.95em;
}
</style>
