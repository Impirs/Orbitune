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
import { ref, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import Footer from '../components/Footer.vue'
import Sidebar from '../components/Sidebar.vue'
import HomeContent from './HomeContent.vue'
import PlaylistsContent from './PlaylistsContent.vue'
import SettingsContent from './SettingsContent.vue'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.currentUser ? { name: userStore.currentUser } : null)

const selected = ref('Home')
const componentMap = {
  Home: HomeContent,
  Playlists: PlaylistsContent,
  Settings: SettingsContent,
}
const currentComponent = computed(() => componentMap[selected.value])

function onSelect(name) {
  selected.value = name
}

function logout() {
  userStore.logout()
  router.push('/')
}
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
  min-height: 100%; /* 48px navbar, 200px footer */
  background: #faf9f9;
  overflow-y: auto;
  padding: 0;
}
</style>
