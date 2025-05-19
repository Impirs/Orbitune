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
import ContentSpotify from './Content_Spotify.vue'
import ContentYouMusic from './Content_YouMusic.vue'
import ContentDiscover from './Content_Discover.vue'
import ContentSettings from './Content_Settings.vue'

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
  Discover: ContentDiscover,
  'Spotify': ContentSpotify,
  'Youtube Music': ContentYouMusic,
  Settings: ContentSettings,
}
const currentComponent = computed(() => componentMap[selected.value] || HomeContent)

function setTab(tab) {
  selected.value = tab in componentMap ? tab : 'Home';
}

function onSelect(name) {
  selected.value = name;
  // Можно добавить query/tab если нужно
}

// Следим за query.tab (если нужно)
watch(
  () => route.query.tab,
  (tab) => {
    if (tab && tab !== selected.value) setTab(tab);
  },
  { immediate: true }
)
</script>

<style scoped>
.userhome-root {
  display: flex;
  flex-direction: column;
}
.userhome-main {
  flex: 1 1 auto;
  height: calc(100vh - 64px);
  display: flex;
  position: relative;
  min-height: 0;
  background: #0f1225;
}
.userhome-content {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 100%;
  background: #0f1225;
  overflow-y: auto;
  padding: 0;
}
</style>
