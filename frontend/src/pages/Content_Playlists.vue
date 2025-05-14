<template>
  <div class="content-playlists">
    <h2>Spotify</h2>
    <div v-if="userStore.loading" class="loader">Loading playlists...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <div v-else>
      <div v-if="!spotifyPlaylists || spotifyPlaylists.length === 0" class="no-playlists">No Playlists available</div>
      <div v-else class="playlist-list-block">
        <div v-for="pl in spotifyPlaylists" :key="pl.id" class="playlist-row" @click="openPlaylist('spotify', pl)">
          <div class="playlist-title">{{ pl.title }}</div>
          <div class="playlist-tracks">
            <template v-if="typeof pl.tracks_count === 'number'">
              <span v-if="pl.tracks_count === undefined">...</span>
              <span v-else>{{ pl.tracks_count }} tracks</span>
            </template>
            <template v-else>
              ...
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
const userStore = useUserStore();
const router = useRouter();

const spotifyPlaylists = computed(() => userStore.playlists['spotify'] || []);

onMounted(() => {
  userStore.fetchPlaylists();
});

function openPlaylist(service, playlist) {
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
.no-playlists {
  color: #fff;
  background: #222b36;
  border-radius: 18px;
  padding: 32px 0;
  text-align: center;
  font-size: 1.2em;
  margin-top: 32px;
}
.playlist-list-block {
  background: #19202a;
  border-radius: 32px;
  padding: 24px 0 12px 0;
  margin-top: 0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}
.playlist-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 32px;
  border-bottom: 1px solid #2c3440;
  cursor: pointer;
  font-size: 1.25em;
  font-weight: bold;
  color: #fff;
  transition: background 0.15s;
}
.playlist-row:last-child {
  border-bottom: none;
}
.playlist-row:hover {
  background: #263a2e;
}
.playlist-title {
  font-size: 1.35em;
  font-weight: bold;
}
.playlist-tracks {
  font-size: 1em;
  color: #fff;
  opacity: 0.8;
}
</style>
