<template>
  <div class="collapsible-block">
    <div class="collapsible-header">
      <div style="display: flex; align-items: center; gap: 18px; flex: 1;">
        <slot name="header"></slot>
      </div>
      <div class="collapsible-header-actions" style="display: flex; align-items: center; gap: 12px;">
        <slot name="header-actions"></slot>
      </div>
    </div>
    <transition name="collapsible">
      <div v-show="isOpen" class="collapsible-content">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue';
const isOpen = ref(true);
function toggle() {
  isOpen.value = !isOpen.value;
}
</script>

<style scoped>
.collapsible-block {
  /* background: rgba(15,18,37,0.3); */
  background: rgba(255,255,255,0.3);
  border-radius: 22px;
  padding: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.10);
}
.collapsible-header {
  position: relative;
  border-radius: 22px 22px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between; 
  padding: 12px 24px 22px 24px;

  cursor: default;
  font-size: 1.2em;
  font-weight: bold;
  user-select: none;
}
.collapsible-header::after {
  content: "";
  position: absolute;
  left: 4%;
  right: 4%;
  bottom: 0;
  height: 2px;
  background: rgba(255,255,255);
  pointer-events: none;
}
.collapsible-arrow {
  display: inline-block;
  transition: transform 0.2s;
  margin-right: 10px;
}
.collapsible-arrow.open {
  transform: rotate(90deg);
}
.collapsible-content {
  border-radius: 0 0 22px 22px;
  padding: 0;
  padding-top: 8px;
  min-height: 60px;

  padding-left: 0;
  padding-bottom: 0;
}
.collapsible-enter-active, .collapsible-leave-active {
  transition: max-height 0.25s cubic-bezier(.4,0,.2,1), opacity 0.2s;
}
.collapsible-enter-from, .collapsible-leave-to {
  max-height: 0;
  opacity: 0;
}
.collapsible-enter-to, .collapsible-leave-from {
  max-height: 500px;
  opacity: 1;
}
</style>
