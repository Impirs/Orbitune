<template>
  <div class="platform-playlist">
    <Playlist_bar
      :selectedId="selectedPlaylistId"
      :expanded="expanded"
      @select="onSelectPlaylist"
      @toggle-expanded="toggleExpanded"
      class="playlist-bar-flex"
    />
    <transition name="fade-tracks" mode="out-in">
      <Tracks_list
        v-if="selectedPlaylistId && !expanded"
        :playlistId="selectedPlaylistId"
        class="tracks-list-flex"
        key="tracks-list"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useUserStore } from '../stores/user';
import Playlist_bar from './Playlist_bar.vue';
import Tracks_list from './Tracks_list.vue';
const userStore = useUserStore();

const selectedPlaylistId = ref(null);
const expanded = ref(false);

const playlists = computed(() => userStore.playlists['spotify'] || []);
const favoritesPlaylistId = computed(() => userStore.favoritesPlaylistId);

watch([playlists, favoritesPlaylistId], ([pls, favId]) => {
  if (!selectedPlaylistId.value && favId) {
    selectedPlaylistId.value = favId;
  }
}, { immediate: true });

function onSelectPlaylist(id) {
  selectedPlaylistId.value = id;
  // Если был expanded, возвращаемся в default (expanded = false)
  if (expanded.value) expanded.value = false;
}
function toggleExpanded() {
  expanded.value = !expanded.value;
}
</script>

<style scoped>
.platform-playlist {
  display: flex;
  flex-direction: row;
  position: relative;
  width: 100%;
  height: 100%;
  gap: 0;
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px) saturate(2);
  /* -webkit-backdrop-filter: blur(8px) saturate(1); */
  border: 1px solid rgba(255,255,255,0.33);
  min-height: 0;
  min-width: 0;
  align-items: stretch;
}
.playlist-bar-flex {
  flex: 0 0 340px;
  min-width: 320px;
  max-width: 420px;
  height: calc(100% - 36px);
  min-height: 0;
}
.tracks-list-flex {
  flex: 1 1 0;
  min-width: 0;
  height: calc(100% - 36px);
  min-height: 0;
  /* fade animation will handle display */
}
.fade-tracks-enter-active, .fade-tracks-leave-active {
  transition: opacity 0.25s cubic-bezier(0.4,0,0.2,1);
}
.fade-tracks-enter-from, .fade-tracks-leave-to {
  opacity: 0;
}
</style>
