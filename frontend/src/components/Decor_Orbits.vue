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
      :style="planetStyleAnimated(idx, planet.size)"
    >
      <Decor_Planets :type="planet.type" :size="planet.size" />
    </div>
  </div>
</template>

<script setup>
import Decor_Planets from './Decor_Planets.vue'
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  radius: { type: Number, default: 80 },
  strokeWidth: { type: Number, default: 2 },
  color: { type: String, default: '#bdbdbd' },
  size: { type: Number, default: 200 },
  planets: {
    type: Array,
    default: () => [] // [{type: 'purple', size: 1, angle: 0}, ...]
  }
})

const animatedAngles = ref([])
const frameId = ref(null)

function startSwayAnimation() {
  const swayRange = 10
  const swayDuration = 60
  let startTime = performance.now()

  function animate() {
    const now = performance.now()
    const planetsCount = props.planets.length
    animatedAngles.value = props.planets.map((planet, idx) => {
      // Индивидуальная задержка
      const delay = idx * 10000
      const t = ((now - startTime - delay) / (swayDuration * 1000)) % 2
      let sway = 0
      if (t < 0) sway = -swayRange
      else if (t < 1) sway = -swayRange + (t * 2 * swayRange)
      else if (t < 2) sway = swayRange - ((t - 1) * 2 * swayRange)
      else sway = -swayRange
      return planet.angle + sway
    })
    frameId.value = requestAnimationFrame(animate)
  }
  frameId.value = requestAnimationFrame(animate)
}

onMounted(() => {
  startSwayAnimation()
})

onUnmounted(() => {
  if (frameId.value) cancelAnimationFrame(frameId.value)
})

watch(() => props.planets, () => {
  nextTick(() => startSwayAnimation())
})

function planetStyle(angle, planetSize) {
  const r = props.radius
  const center = props.size / 2
  const rad = (angle - 90) * Math.PI / 180
  const basePlanet = 120 * planetSize
  const x = Math.round((center + r * Math.cos(rad) - basePlanet / 2) * 2) / 2
  const y = Math.round((center + r * Math.sin(rad) - basePlanet / 2) * 2) / 2
  return {
    position: 'absolute',
    left: 0,
    top: 0,
    width: basePlanet + 'px',
    height: basePlanet + 'px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    pointerEvents: 'none',
    transform: `translate3d(${x}px, ${y}px, 0)`,
    transition: 'transform 0.5s',
    willChange: 'transform',
    backfaceVisibility: 'hidden',
  }
}

function planetAnimStyle(idx) {
  // idx: индекс планеты на орбите
  return {
    animation: `orbit-sway 10s ease-in-out infinite alternate`,
    animationDelay: `${idx * 3}s`,
    willChange: 'transform',
  }
}

function planetStyleAnimated(idx, planetSize) {
  const angle = animatedAngles.value[idx] ?? (props.planets[idx]?.angle ?? 0)
  return planetStyle(angle, planetSize)
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
@keyframes orbit-sway {
  0% { transform: rotate(-10deg); }
  50% { transform: rotate(10deg); }
  100% { transform: rotate(-10deg); }
}
.planet-on-orbit {
  position: absolute;
  z-index: 2;
  /* transition уже в style */
  /* Анимация покачивания */
}
</style>
