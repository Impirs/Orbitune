<template>
  <div class="content-player" ref="rootRef">
    <h2>Player</h2>
    <div v-if="userStore.loading" class="loader">Loading tracks...</div>
    <div v-else-if="userStore.error" class="error-block">{{ userStore.error }}</div>
    <div v-else-if="!playlist && !isFavorites">
      <p>Select a playlist to view tracks.</p>
    </div>
    <div v-else>
      <h3 v-if="isFavorites">Favorites</h3>
      <h3 v-else>{{ playlist.title }} <span style="color:#888;font-size:0.9em;">({{ service }})</span></h3>
      <div v-if="playlistTracksLoading" class="loader">Loading tracks...</div>
      <div v-else-if="playlistTracksError" class="error-block">{{ playlistTracksError }}</div>
      <ul v-else>
        <li v-for="track in tracksToShow" :key="track.id || track.title">
          {{ track.title }} — {{ track.artist }}
        </li>
      </ul>
      <div v-if="tracksToShow.length === 0 && !playlistTracksLoading && !playlistTracksError" style="color:#888;">No tracks in playlist.</div>
      <div v-if="isFavorites && canLoadMore" class="loader" style="text-align:center;">Loading more...</div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '../stores/user';
const userStore = useUserStore();
const route = useRoute();

const service = computed(() => route.query.service || '');
const playlistId = computed(() => route.query.playlistId);
const favoritesPlaylistId = computed(() => userStore.favoritesPlaylistId);

// --- Сохраняем/восстанавливаем последний выбранный плейлист ---
const lastSelectedPlaylistId = ref(localStorage.getItem('lastSelectedPlaylistId'));
watch(
  () => [service.value, playlistId.value],
  ([s, pid]) => {
    if (s && pid) {
      lastSelectedPlaylistId.value = pid;
      localStorage.setItem('lastSelectedPlaylistId', pid);
      userStore.lastSelectedPlaylist = pid;
    }
  },
  { immediate: true }
);

// --- Корректный выбор плейлиста избранного ---
const isFavorites = computed(() => {
  // Если явно выбран плейлист — не favorites
  if (service.value && playlistId.value) return false;
  // Если есть favoritesPlaylistId — используем его
  return true;
});

const playlist = computed(() => {
  if (isFavorites.value && favoritesPlaylistId.value) {
    // Находим плейлист избранного по точному id для выбранной платформы
    const pls = userStore.playlists[service.value] || [];
    return pls.find(pl => String(pl.id) === String(favoritesPlaylistId.value));
  }
  if (!service.value || !playlistId.value) return null;
  const pls = userStore.playlists[service.value] || [];
  return pls.find(pl => String(pl.id) === String(playlistId.value));
});
const tracksToShow = computed(() => {
  if (isFavorites.value && service.value && userStore.favorites[service.value]) return userStore.favorites[service.value];
  if (!isFavorites.value && playlist.value) return playlist.value.tracks || [];
  return [];
});

// --- Ленивая подгрузка избранных треков ---
const favoritesLimit = 50;
const loadingMore = ref(false);
const canLoadMore = computed(() => {
  return isFavorites.value && userStore.favorites && userStore.favorites.length < (userStore.favoritesTotal || 0);
});

async function loadMoreFavorites() {
  if (!canLoadMore.value || loadingMore.value) return;
  loadingMore.value = true;
  await userStore.fetchFavoritesLazy(userStore.favorites.length, favoritesLimit);
  loadingMore.value = false;
}

function onScroll(e) {
  if (!canLoadMore.value) return;
  const el = e.target;
  if (el.scrollHeight - el.scrollTop - el.clientHeight < 120) {
    loadMoreFavorites();
  }
}

const rootRef = ref(null);
onMounted(() => {
  if (service.value && playlistId.value) {
    userStore.lastSelectedPlaylist = playlistId.value;
  } else {
    const last = localStorage.getItem('lastSelectedPlaylistId');
    if (last && userStore.playlists['spotify'] && userStore.playlists['spotify'].some(pl => String(pl.id) === String(last))) {
      const q = { ...route.query, service: 'spotify', playlistId: last };
      if (!route.query.playlistId || String(route.query.playlistId) !== String(last)) {
        import('../router').then(({ default: router }) => {
          router.replace({ path: route.path, query: q });
        });
      }
    }
  }
  if (isFavorites.value && service.value) {
    userStore.fetchFavoritesLazy(0, favoritesLimit, service.value);
  }
  nextTick(() => {
    if (rootRef.value) {
      rootRef.value.addEventListener('scroll', onScroll);
    }
  });
});
onUnmounted(() => {
  if (rootRef.value) {
    rootRef.value.removeEventListener('scroll', onScroll);
  }
});

const playlistTracksLoading = ref(false);
const playlistTracksError = ref('');

watch(
  () => [service.value, playlistId.value],
  async ([s, pid], oldVals) => {
    if (!isFavorites.value && playlist.value && (!playlist.value.tracks || playlist.value.tracks.length === 0)) {
      playlistTracksLoading.value = true;
      playlistTracksError.value = '';
      try {
        await userStore.fetchPlaylistTracks(playlist.value.id, s);
      } catch (e) {
        playlistTracksError.value = e?.message || 'Failed to load tracks';
      } finally {
        playlistTracksLoading.value = false;
      }
    }
    if (isFavorites.value && s) {
      userStore.fetchFavoritesLazy(0, favoritesLimit, s);
    }
  },
  { immediate: true }
);
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
