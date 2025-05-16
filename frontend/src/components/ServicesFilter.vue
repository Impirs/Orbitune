<template>
  <div class="services-filter-wrapper" ref="wrapper">
    <button class="services-filter-btn" @click.stop="toggleDropdown">
      {{ selectedLabel }}
      <span class="arrow" :class="{ open: isOpen }">▼</span>
    </button>
    <div v-if="isOpen" class="services-filter-dropdown">
      <div v-for="option in options" :key="option" class="services-filter-option" @click="select(option)">
        {{ option }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
const props = defineProps({
  options: Array,
  modelValue: String
});
const emit = defineEmits(['update:modelValue']);
const isOpen = ref(false);
const wrapper = ref(null);
const selectedLabel = computed(() => props.modelValue || props.options[0]);
function toggleDropdown() {
  isOpen.value = !isOpen.value;
}
function select(option) {
  emit('update:modelValue', option);
  isOpen.value = false;
}
function handleClickOutside(e) {
    if (wrapper.value && !wrapper.value.contains(e.target)) {
        isOpen.value = false;
    }
}
onMounted(() => {
    document.addEventListener('mousedown', handleClickOutside);
});
onBeforeUnmount(() => {
    document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<style scoped>
.services-filter-wrapper {
    position: relative;
    display: inline-block;
}
.services-filter-btn {
    background: rgba(255,255,255,0.30);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 8px 18px;
    font-size: 1.1em;
    cursor: pointer;
    min-width: 80px;
    display: flex;
    align-items: center;
    justify-content: end;
    gap: 8px;
}
.arrow {
    font-size: 0.9em;
    transition: transform 0.2s;
}
.arrow.open {
    transform: rotate(180deg);
}
.services-filter-dropdown {
    position: absolute;
    left: 0;
    top: 110%;
    background: rgba(255,255,255,0.30);
    color: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.18);
    min-width: 120px;
    z-index: 1000;
    padding: 10px 5px;
}
.services-filter-option {
    padding: 8px 18px;
    cursor: pointer;
    transition: background 0.15s;
}
.services-filter-option:hover {
    background: rgba(255,255,255,0.9);
}
</style>
