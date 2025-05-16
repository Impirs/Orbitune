<template>
  <div class="playlist-row" @click="handleClick">
    <div class="playlist-title">{{ playlist.title }}</div>
    <div class="playlist-tracks">
      <template v-if="typeof playlist.tracks_count === 'number'">
        <span v-if="playlist.tracks_count === undefined">...</span>
        <span v-else>{{ playlist.tracks_count }} tracks</span>
      </template>
      <template v-else>
        ...
      </template>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';
const props = defineProps({
  playlist: { type: Object, required: true }
});
const emit = defineEmits(['open']);
function handleClick() {
  // Логируем id и тип
  console.log('[PlaylistRow] click', props.playlist.id, typeof props.playlist.id, props.playlist);
  emit('open', props.playlist);
}
</script>

<style scoped>
.playlist-row {
  display: flex;
  position: relative;
  justify-content: space-between;
  align-items: center;
  padding: 18px 32px;
  border-bottom: 1px solid transparent;
  cursor: pointer;
  font-size: 1.25em;
  font-weight: bold;
  color: #fff;
  transition: background 0.15s;
}
.playlist-row::after {
  content: "";
  position: absolute;
  left: 4%;
  right: 4%;
  bottom: 0;
  height: 1px;
  background: rgba(255,255,255);
  pointer-events: none;
}
.playlist-row:last-child::after {
  display: none;
}
.playlist-row:last-child {
  border-bottom: none;
}
.playlist-row:hover {
  background: rgba(255,255,255,0.30);
}
.playlist-title {
  font-size: 1.35em;
  font-weight: bold;
}
.playlist-tracks {
  font-size: 1em;
  color: #fff;
  opacity: 0.8;
}
</style>
