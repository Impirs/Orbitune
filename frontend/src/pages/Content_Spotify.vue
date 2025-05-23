<template>
  <div class="content-spotify">
    <Platform_Playlist platform="spotify" />
    <Platform_Player platform="spotify" />
  </div>
</template>

<script setup>
import Platform_Playlist from '../components/Platform_Playlist.vue';
import Platform_Player from '../components/Platform_Player.vue';
// Content_Spotify: logic for Spotify platform will be added later
</script>

<style scoped>
.content-spotify {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
}
</style>
