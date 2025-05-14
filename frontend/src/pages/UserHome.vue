<template>
  <div class="userhome-root">
    <Navbar :user="user" />
    <div class="userhome-main">
      <Sidebar :selected="selected" @select="onSelect" />
      <main class="userhome-content">
        <component :is="currentComponent" />
      </main>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import Sidebar from '../components/Sidebar.vue'

import HomeContent from './Content_Home.vue'
import PlaylistsContent from './Content_Playlists.vue'
import SettingsContent from './Content_Settings.vue'
import PlatformsContent from './Content_Platforms.vue'
import PlayerContent from './Content_Player.vue'

import { ref, computed, watch } from 'vue'
import { useUserStore } from '../stores/user'
import { useRouter, useRoute } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const user = computed(() => userStore.currentUser ? { name: userStore.currentUser } : null)

const selected = ref('Home')
const componentMap = {
  Home: HomeContent,
  Playlists: PlaylistsContent,
  Player: PlayerContent,
  Platforms: PlatformsContent,
  Settings: SettingsContent,
}
const currentComponent = computed(() => componentMap[selected.value])

// Синхронизация selected <-> query.tab
function setTab(tab) {
  selected.value = tab in componentMap ? tab : 'Home';
  // если tab не совпадает — fallback
}

// При выборе в сайдбаре — меняем query
function onSelect(name) {
  if (name !== selected.value) {
    router.push({
      path: route.path,
      query: { tab: name } // только tab, без player/playlists/service
    });
  }
  selected.value = name;
}

// Следим за query.tab
watch(
  () => route.query.tab,
  (tab) => {
    if (tab && tab !== selected.value) setTab(tab);
  },
  { immediate: true }
);

// Автоматический переход в Player по query
watch(() => route.query, (q) => {
  if (q.player) {
    setTab('Player');
  } else if (q.playlists) {
    setTab('Playlists');
  } else if (q.settings) {
    setTab('Settings');
  } else if (q.tab) {
    setTab(q.tab);
  }
})
</script>

<style scoped>
.userhome-root {
  display: flex;
  flex-direction: column;
}
.userhome-main {
  flex: 1 1 auto;
  height: calc(100vh - 48px);
  display: flex;
  min-height: 0;
  background: #faf9f9;
}
.userhome-content {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 100%;
  background: #faf9f9;
  overflow-y: auto;
  padding: 0;
}
</style>
