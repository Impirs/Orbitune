<template>
  <nav class="sidebar">
    <ul>
      <li v-for="item in sidebarItems" :key="item.name" :class="{active: selected === item.name}" :data-tab="item.name" @click="$emit('select', item.name)">
        <img v-if="item.imagePath" :src="item.imagePath" class="sidebar_icon" />
        <span v-else class="icon"></span>
        <div class="label_btn">
          <span class="label">{{ item.label }}</span>
        </div>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { defineProps, computed } from 'vue'
import { useUserStore } from '../stores/user'
const props = defineProps({
  selected: String
})
const userStore = useUserStore();

const baseTabs = [
  { name: 'Home', label: 'Home', imagePath: new URL('../assets/sun.png', import.meta.url).href },
  { name: 'Discover', label: 'Discover', imagePath: new URL('../assets/satellite.png', import.meta.url).href },
  { name: 'Settings', label: 'Settings', imagePath: new URL('../assets/black_hole.png', import.meta.url).href }
];

// Platform content tabs (Spotify, Youtube Music)
const serviceTabs = computed(() => {
  const result = [];
  const connected = userStore.connectedServices || [];
  // Discover -> Spotify, Youtube Music -> Settings
  if (connected.some(s => s.platform === 'spotify')) {
    result.push({ name: 'Spotify', label: 'Spotify', imagePath: new URL('../assets/earth.png', import.meta.url).href }); 
  }
  if (connected.some(s => s.platform === 'google')) {
    result.push({ name: 'Youtube Music', label: 'Youtube Music', imagePath: new URL('../assets/mars.png', import.meta.url).href });
  }
  return result;
});

const sidebarItems = computed(() => {
  const items = [baseTabs[0], baseTabs[1]];
  serviceTabs.value.forEach(tab => items.push(tab));
  items.push(baseTabs[2]);
  return items;
});
</script>

<style scoped>
.sidebar {
  display: flex;
  color: #fff;
  flex-direction: column;
  width: 320px;
  height: calc(100% - 64px);
  padding: 32px 0 32px 42px; 
  position: relative;
}
.sidebar::before {
  content: '';
  position: absolute;
  left: 63px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #fff0 0%, #fff1 5%, #fff2 25%, #fff1 90%, #fff0 100%);
  border-radius: 2px;
  z-index: 0;
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
li {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  z-index: 1;
  transition: none;
}
li:last-child {
  margin-top: auto;
}
.sidebar_icon, .icon {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  margin-right: 16px;
  background: #ff4444;
  z-index: 2;
}
.sidebar_icon {
  object-fit: contain;
  background: none;
}
.label_btn {
  margin-left: 0;
  padding: 18px 36px;
  display: flex;
  align-items: center;
  min-width: 120px;
  width: 182px;
  user-select: none;
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 18px;
  box-shadow: 0 2px 32px 0 rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(8px) saturate(2);
  /* -webkit-backdrop-filter: blur(8px) saturate(1); */
  border: 1px solid rgba(255,255,255,0.33);
  transition: background 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.38s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
li .label_btn:hover {
  background: rgba(255, 255, 255, 0.28);
  transform: translateX(8px);
}
li .label_btn:active {
  background: rgba(255, 255, 255, 0.38);
  transform: translateX(16px);
}
li.active .label_btn {
  background: #ffeaea;
  color: #000;
  font-weight: 600;
  /* transform: translateX(8px); */
}
li.active .label_btn:hover {
  /* background: inherit; */
  /* transform: none; */
}
li.active[data-tab="Spotify"] .label_btn {
  background: #1db954; /* 98e478 */
  color: #222;
}
li.active[data-tab="Youtube Music"] .label_btn {
  background: #f40d3d; /* cd3d38 */
  color: #fff;
}
li.active[data-tab="Home"] .label_btn {
  background: #ee8027; /* f09433 */
  color: #fff;
}
.label {
  font-size: 1.3em;
  font-weight: 500;
}
</style>
