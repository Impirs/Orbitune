<template>
  <div class="orbit-wrapper" :style="{ width: size + 'px', height: size + 'px' }">
    <svg :width="size" :height="size" class="orbit-svg">
      <circle
        :cx="size/2"
        :cy="size/2"
        :r="radius"
        fill="none"
        :stroke="color"
        :stroke-width="strokeWidth"
      />
    </svg>
    <div
      v-for="(planet, idx) in planets"
      :key="idx"
      class="planet-on-orbit"
      :style="planetStyle(planet.angle, planet.size)"
    >
      <Decor_Planets :type="planet.type" :size="planet.size" />
    </div>
  </div>
</template>

<script setup>
import Decor_Planets from './Decor_Planets.vue'

const props = defineProps({
  radius: { type: Number, default: 80 },
  strokeWidth: { type: Number, default: 2 },
  color: { type: String, default: '#bdbdbd' },
  size: { type: Number, default: 200 }, // размер контейнера
  planets: {
    type: Array,
    default: () => [] // [{type: 'purple', size: 1, angle: 0}, ...]
  }
})

function planetStyle(angle, planetSize) {
  const r = props.radius
  const center = props.size / 2
  const rad = (angle - 90) * Math.PI / 180 // -90 чтобы 0° был сверху
  const basePlanet = 120 * planetSize // базовый размер планеты
  const x = center + r * Math.cos(rad) - basePlanet / 2
  const y = center + r * Math.sin(rad) - basePlanet / 2
  return {
    position: 'absolute',
    left: x + 'px',
    top: y + 'px',
    transition: 'left 0.5s, top 0.5s',
    width: basePlanet + 'px',
    height: basePlanet + 'px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    pointerEvents: 'none',
  }
}
</script>

<style scoped>
.orbit-wrapper {
  position: relative;
  display: inline-block;
}
.orbit-svg {
  position: absolute;
  left: 0;
  top: 0;
  z-index: 1;
}
.planet-on-orbit {
  position: absolute;
  z-index: 2;
  /* transition уже в style */
}
</style>
