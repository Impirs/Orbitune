<template>
  <div :class="['playlist-bar', expanded ? 'expanded' : 'default']">
    <div class="playlist-bar-header">
      <span class="playlist-bar-title">Playlists</span>
      <button class="playlist-bar-create">
        <img src="https://img.icons8.com/?size=100&id=62888&format=png&color=ffffff">
        Create
      </button>
      <button class="playlist-bar-toggle" @click="$emit('toggle-expanded')">
        <img v-if="expanded" src="https://img.icons8.com/?size=100&id=78831&format=png&color=ffffff" alt="Collapse" style="width:20px;height:20px;" />
        <img v-else src="https://img.icons8.com/?size=100&id=78833&format=png&color=ffffff" alt="Expand" style="width:20px;height:20px;" />
      </button>
    </div>
    <div v-if="expanded" class="playlist-grid playlist-scrollable">
      <div
        v-for="pl in orderedPlaylists"
        :key="pl.id"
        class="playlist-grid-item"
        :class="{ selected: pl.id === selectedId }"
        @click="selectPlaylist(pl.id)"
      >
        <img :src="pl.image_url || fallbackCover" class="playlist-cover" />
        <div class="playlist-title">{{ pl.title }}</div>
        <div class="playlist-count">
          {{ pl.tracks_number ?? pl.tracks_count ?? 0 }} tracks
        </div>
      </div>
    </div>
    <div v-else class="playlist-list playlist-scrollable">
      <div
        v-for="pl in orderedPlaylists"
        :key="pl.id"
        class="playlist-list-item"
        :class="{ selected: pl.id === selectedId }"
        @click="selectPlaylist(pl.id)"
      >
        <img :src="pl.image_url || fallbackCover" class="playlist-cover" />
        <div class="playlist-info">
          <div class="playlist-title">{{ pl.title }}</div>
          <div class="playlist-count">
            {{ pl.tracks_number ?? pl.tracks_count ?? 0 }} tracks
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useUserStore } from '../stores/user'
const userStore = useUserStore()
const fallbackCover = new URL('../assets/music_universe.png', import.meta.url)
  .href
const props = defineProps({
  selectedId: Number,
  expanded: Boolean
})
const emit = defineEmits(['select', 'toggle-expanded'])

const playlists = computed(() => userStore.playlists['spotify'] || []);
const favoritesPlaylistExternalId = computed(() => userStore.favoritesPlaylistExternalId);
const favoritesPlaylist = computed(() => {
  const pls = playlists.value;
  if (!pls.length || !favoritesPlaylistExternalId.value) {
    return null;
  }
  const found = pls.find(pl => String(pl.external_id) === String(favoritesPlaylistExternalId.value)) || null;
  return found;
});
const orderedPlaylists = computed(() => {
  const fav = favoritesPlaylist.value;
  let rest = playlists.value;
  if (fav) {
    rest = playlists.value.filter(pl => String(pl.external_id) !== String(fav.external_id));
  }
  rest = rest.slice().sort((a, b) => Number(a.id) - Number(b.id));
  return fav ? [fav, ...rest] : rest;
})

function selectPlaylist(id) {
  emit('select', id)
}
</script>

<style scoped>
.playlist-bar {
  display: flex;
  flex-direction: column;
  padding: 18px 16px;
  min-width: 320px;
  max-width: 420px;
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1),
  min-width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.playlist-bar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px 18px 24px;
}
.playlist-bar-title {
  font-size: 1.7em;
  font-weight: bold;
  flex: 1 1 auto;
}
.playlist-bar-create {
  display: flex;
  background: rgba(255, 255, 255, 0.18);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 1.3em;
  padding: 6px 16px 6px 12px;
  cursor: pointer;
  transition: background 0.18s;
  justify-content: center;
  align-content: baseline;
  justify-content: baseline;
  gap: 4px;
}
.playlist-bar-create img{
    width: 16px;
    height: 16px;
}
.playlist-bar-create:hover {
  background: rgba(255, 255, 255, 0.32);
}
.playlist-bar-toggle {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px 6px;
  border-radius: 50%;
  transition: background 0.18s;
  align-content: center;
  justify-content: center;
}
.playlist-bar-toggle:hover {
  background: rgba(255, 255, 255, 0.18);
}
.playlist-scrollable {
  overflow-y: auto;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s cubic-bezier(0.4,0,0.2,1);
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.playlist-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 12px;
  overflow-y: scroll;
  overflow-x: hidden;
}
.playlist-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 12px;
  border-radius: 14px;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s;
  background: none;
}
.playlist-list-item.selected,
.playlist-list-item:hover {
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
}
.playlist-list-item:hover {
  transform: translateX(8px);
}
.playlist-cover {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  object-fit: cover;
  background: #222;
}
.playlist-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.playlist-title {
  font-size: 1.1em;
  font-weight: 500;
  color: #fff;
}
.playlist-count {
  font-size: 0.98em;
  color: #bbb;
}
.playlist-bar.collapsed .playlist-info {
  display: none;
}
.playlist-bar.collapsed .playlist-list-item {
  min-width: 54px;
  max-width: 54px;
  padding: 10px 0;
  justify-content: center;
}
.playlist-bar.expanded {
  min-width: 100%;
  max-width: 100%;
  background: rgba(30, 30, 40, 0.65);
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  border-radius: 20px;
  padding: 18px 0 18px 0;
}
.playlist-bar.expanded .playlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  padding: 0 32px;
}
.playlist-grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: none;
  border-radius: 18px;
  padding: 18px 8px 12px 8px;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s;
}
.playlist-grid-item.selected,
.playlist-grid-item:hover {
  background: rgba(255, 255, 255, 0.18);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  transform: translateY(-6px) scale(1.04);
}
.playlist-grid-item .playlist-cover {
  width: 120px;
  height: 120px;
  border-radius: 18px;
  margin-bottom: 12px;
}
.playlist-grid-item .playlist-title {
  font-size: 1.08em;
  font-weight: 500;
  color: #fff;
  margin-bottom: 2px;
  text-align: center;
}
.playlist-grid-item .playlist-count {
  font-size: 0.98em;
  color: #bbb;
  text-align: center;
}
</style>
