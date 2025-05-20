<template>
  <div class="userhome-root">
    <Navbar :user="user" />
    <div class="userhome-main">
      <!-- Decorative Orbits on background -->
      <Decor_Orbits
        class="decor-orbit decor-orbit-1"
        :radius="220"
        :size="500"
        color="#23253a"
        :strokeWidth="2"
        :planets="[{type: 'red', size: 0.9, angle: 120}]"
      />
      <Decor_Orbits
        class="decor-orbit decor-orbit-2"
        :radius="400"
        :size="800"
        color="#23253a"
        :strokeWidth="2"
        :planets="[
          {type: 'gray', size: 0.6, angle: 280},
          {type: 'purple', size: 1, angle: 30}
        ]"
      />
      <Decor_Orbits
        class="decor-orbit decor-orbit-3"
        :radius="400"
        :size="800"
        color="#23253a"
        :strokeWidth="2"
        :planets="[
          {type: 'yellow', size: 1, angle: 190},
          {type: 'blue', size: 0.9, angle: 250}
        ]"
      />
      <!-- Main content -->
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
import Decor_Orbits from '../components/Decor_Orbits.vue'

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
  background: inherit;
  overflow: hidden;
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
.decor-orbit {
  position: absolute;
  pointer-events: none;
  z-index: 0;
}
.decor-orbit-1 {
  left: -90px;
  top: -160px;
}
.decor-orbit-2 {
  left: 280px;
  bottom: -380px;
}
.decor-orbit-3 {
  right: -200px;
  top: -280px;
}
</style>
