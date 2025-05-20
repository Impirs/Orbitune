<template>
  <div class="content-spotify">
    <Platform_Playlist />
    <Platform_Player />
  </div>
</template>

<script setup>
import Platform_Playlist from '../components/Platform_Playlist.vue';
import Platform_Player from '../components/Platform_Player.vue';
// Content_Spotify: logic for Spotify platform will be added later
</script>

<style scoped>
.content-spotify {
  width: calc(100% - 64px);
  height: calc(100% - 64px);
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: row;
  padding: 32px;
  overflow: hidden;
}
</style>
