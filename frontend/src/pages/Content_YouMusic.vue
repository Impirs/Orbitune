<template>
  <div class="content-youmusic">
    <Platform_Playlist platform="youtube" />
    <Platform_Player platform="youtube" />
  </div>
</template>

<script setup>
import Platform_Playlist from '../components/Platform_Playlist.vue';
import Platform_Player from '../components/Platform_Player.vue';
// Content_YouMusic: logic for YouTube Music platform will be added later
</script>

<style scoped>
.content-youmusic {
  width: 100%;
  height: 100%;
  min-height: 0;
  min-width: 0;
}
</style>
