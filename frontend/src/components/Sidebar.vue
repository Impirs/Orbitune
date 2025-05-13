<template>
  <nav class="sidebar">
    <ul>
      <li v-for="item in items" :key="item.name" :class="{active: selected === item.name}" @click="$emit('select', item.name)">
        <span class="icon"></span>
        <span class="label">{{ item.label }}</span>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { defineProps } from 'vue'
const props = defineProps({
  selected: String
})
const items = [
  { name: 'Home', label: 'Home' },
  { name: 'Playlists', label: 'Playlists' },
  { name: 'Player', label: 'Player' },
  { name: 'Platforms', label: 'Platforms' },
  { name: 'Settings', label: 'Settings' }
]
</script>

<style scoped>
.sidebar {
  width: 180px;
  background: #fff;
  border-right: 1px solid #eee;
  height: 100%;
  padding-top: 32px;
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
li {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  cursor: pointer;
  transition: background 0.2s;
}
li.active, li:hover {
  background: #ffeaea;
}
.icon {
  width: 28px;
  height: 28px;
  background: #ff4444;
  border-radius: 6px;
  margin-right: 16px;
}
.label {
  font-size: 1.1em;
  font-weight: 500;
}
</style>
