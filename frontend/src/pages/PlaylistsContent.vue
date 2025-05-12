<template>
  <div class="content-playlists">
    <h2>Playlists</h2>
    <div v-if="userStore.playlists.length === 0">No playlists found.</div>
    <ul v-else>
      <li v-for="pl in userStore.playlists" :key="pl.id">
        <div class="playlist-title">{{ pl.title }}</div>
        <div class="playlist-platform">Platform: {{ pl.source_platform || 'local' }}</div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();

onMounted(() => {
  userStore.fetchPlaylists();
});
</script>

<style scoped>
.content-playlists {
  padding: 32px;
}
ul {
  margin-top: 18px;
  padding: 0;
  list-style: none;
}
li {
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
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
