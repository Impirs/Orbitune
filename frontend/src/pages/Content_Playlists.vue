<template>
  <div class="content-playlists">
    <CollapsibleBlock>
      <template #header>
        <span style="color:#1db954;font-size:1.3em;margin-right:8px;">&#9835;</span> 
        <span style="font-size:1.4em">Playlists</span>
      </template>
      <template #header-actions>
        <ServicesFilter
          v-model="selectedService"
          :options="serviceOptions"
        />
        <button class="create-btn" @click="onCreatePlaylist">Create new</button>
      </template>
      <template #default>
        <div v-if="userStore.loading" class="loader">Loading playlists...</div>
        <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
        <div v-else>
          <div v-if="!filteredPlaylists.length" class="no-playlists">No Playlists available</div>
          <div class="playlist-list-block-scroll">
            <div class="playlist-list-block">
              <PlaylistRow
                v-for="pl in filteredPlaylists"
                :key="pl.id"
                :playlist="pl"
                @open="openPlaylist(selectedService === 'All' ? 'spotify' : selectedService.toLowerCase(), $event)"
              />
            </div>
          </div>
        </div>
      </template>
    </CollapsibleBlock>
  </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import PlaylistRow from '../components/PlaylistRow.vue';
import CollapsibleBlock from '../components/CollapsibleBlock.vue';
import ServicesFilter from '../components/ServicesFilter.vue';
const userStore = useUserStore();
const router = useRouter();

const selectedService = ref('All');
const serviceOptions = computed(() => {
  const base = ['All'];
  const connected = userStore.connectedServices?.map(s => {
    if (s.platform === 'google') return 'Youtube';
    if (s.platform === 'yandex') return 'Yandex';
    if (s.platform === 'spotify') return 'Spotify';
    return s.platform.charAt(0).toUpperCase() + s.platform.slice(1);
  }) || [];
  return [...base, ...connected.filter((v, i, arr) => arr.indexOf(v) === i)];
});

const spotifyPlaylists = computed(() => userStore.playlists['spotify'] || []);
const yandexPlaylists = computed(() => userStore.playlists['yandex'] || []);
const youtubePlaylists = computed(() => userStore.playlists['google'] || []);
const allPlaylists = computed(() => [
  ...spotifyPlaylists.value,
  ...yandexPlaylists.value,
  ...youtubePlaylists.value
]);
const filteredPlaylists = computed(() => {
  if (selectedService.value === 'All') return allPlaylists.value;
  if (selectedService.value === 'Spotify') return spotifyPlaylists.value;
  if (selectedService.value === 'Yandex') return yandexPlaylists.value;
  if (selectedService.value === 'Youtube') return youtubePlaylists.value;
  return allPlaylists.value;
});

onMounted(() => {
  userStore.fetchPlaylists();
});

function openPlaylist(service, playlist) {
  router.replace({ name: 'UserHome', query: { player: 1, service, playlistId: playlist.id } });
}
function onCreatePlaylist() {
  alert('/TODO add creating simple or mixed playlist');
}
</script>

<style scoped>
.content-playlists {
  padding: 32px;
  background: #0f1225;
  height: calc(100% - 64px);
  display: flex;
  flex-direction: column;
}
.collapsible-block {
  height: 100%;
  flex-direction: column;
  min-height: 0;
}
.create-btn {
  background: rgba(255,255,255,0.50);
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 8px 18px;
  font-size: 1.1em;
  cursor: pointer;
  margin-left: 10px;
  transition: background 0.15s;
}
.create-btn:hover {
  background: rgba(255,255,255,0.25);
}
.playlist-list-block-scroll {
  max-height: 78vh;
  height: 100%;
  overflow-y: auto;
  border-radius: 0 0 22px 22px;
  background: transparent;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.playlist-list-block-scroll::-webkit-scrollbar {
  width: 8px;
  background: transparent;
}
.playlist-list-block-scroll::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 8px;
}
.playlist-list-block-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.playlist-list-block {
  background: transparent;
  border-radius: 0 0 22px 22px;
  padding: 0;
  margin-top: 0;
  box-shadow: none;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
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
  background: rgba(15,18,37,0.5);
}
</style>
