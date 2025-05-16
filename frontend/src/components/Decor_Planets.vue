<template>
  <div>
    <!-- Пример использования: -->
    <!-- <DecorPlanet type="purple" :size="1" /> -->
    <!-- <DecorOrbit :radius="80" :strokeWidth="4" /> -->
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Планета с линиями
const planetTypes = {
  purple: {
    baseClass: 'decor-element-purple',
    lines: 7
  },
  blue: {
    baseClass: 'decor-element-blue',
    lines: 7
  },
  red: {
    baseClass: 'decor-element-red',
    lines: 7
  },
  yellow: {
    baseClass: 'decor-element-yellow',
    lines: 8
  },
  gray: {
    baseClass: 'decor-element-gray',
    lines: 7
  }
}

const props = defineProps({
  type: { type: String, default: 'purple' }, // тип планеты
  size: { type: Number, default: 1 }, // множитель размера
  radius: { type: Number, default: 60 }, // радиус орбиты (для DecorOrbit)
  strokeWidth: { type: Number, default: 2 } // толщина линии орбиты
})

const planet = computed(() => planetTypes[props.type] || planetTypes.purple)
const planetSize = computed(() => 120 * props.size)

</script>

<!-- Планета -->
<template v-if="planetTypes[type]">
  <div :class="planet.baseClass" :style="{ width: planetSize + 'px', height: planetSize + 'px' }">
    <div
      v-for="n in planet.lines"
      :key="n"
      class="line"
      :class="'line' + n"
    ></div>
  </div>
</template>

<!-- Орбита -->
<template v-else>
  <svg :width="(radius + strokeWidth) * 2" :height="(radius + strokeWidth) * 2">
    <circle
      :cx="radius + strokeWidth"
      :cy="radius + strokeWidth"
      :r="radius"
      fill="none"
      stroke="#bdbdbd"
      :stroke-width="strokeWidth"
    />
  </svg>
</template>

<style scoped>
.decor-element-purple {
  position: relative;
  background: #634373bf;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-purple .line { position: absolute; background: #b974b2bf; border-radius: 4px; opacity: 0.7; }
.decor-element-purple .line1 { top: 15px; left: -5px; right: 50px; height: 5px; }
.decor-element-purple .line2 { top: 32px; left: 60px; right: -10px; height: 4px; }
.decor-element-purple .line3 { top: 42px; left: -35px; right: 45px; height: 5px; }
.decor-element-purple .line4 { top: 62px; left: 40px; right: -45px; height: 5px; }
.decor-element-purple .line5 { top: 76px; left: -45px; right: 65px; height: 4px; }
.decor-element-purple .line6 { top: 87px; left: 45px; right: -30px; height: 4px; }
.decor-element-purple .line7 { top: 102px; left: 0px; right: 55px; height: 4px; }

.decor-element-blue {
  position: relative;
  background: #639cecbf;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-blue .line { position: absolute; background: #afddf1af; border-radius: 4px; opacity: 0.7; }
.decor-element-blue .line1 { top: 18px; left: 60px; right: 0px; height: 4px; }
.decor-element-blue .line2 { top: 34px; left: -15px; right: 55px; height: 6px; }
.decor-element-blue .line3 { top: 48px; left: 40px; right: -40px; height: 5px; }
.decor-element-blue .line4 { top: 66px; left: -45px; right: 30px; height: 4px; }
.decor-element-blue .line5 { top: 80px; left: 65px; right: -25px; height: 6px; }
.decor-element-blue .line6 { top: 92px; left: -30px; right: 50px; height: 5px; }
.decor-element-blue .line7 { top: 106px; left: 50px; right: 5px; height: 4px; }

.decor-element-red {
  position: relative;
  background: #f2412ebf;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-red .line { position: absolute; background: #f97c78af; border-radius: 4px; opacity: 0.7; }
.decor-element-red .line1 { top: 16px; left: 35px; right: -30px; height: 6px; }
.decor-element-red .line2 { top: 32px; left: -20px; right:  60px; height: 4px; }
.decor-element-red .line3 { top: 48px; left: 45px; right: -20px; height: 5px; }
.decor-element-red .line4 { top: 60px; left: -45px; right:  65px; height: 6px; }
.decor-element-red .line5 { top: 78px; left: 75px; right: -40px; height: 5px; }
.decor-element-red .line6 { top: 88px; left: -20px; right: 55px; height: 6px; }
.decor-element-red .line7 { top: 106px; left: 65px; right: -10px; height: 4px; }

.decor-element-yellow {
  position: relative;
  background: #cc9165bf;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-yellow .line { position: absolute; background: #f9c564af; border-radius: 4px; opacity: 0.7; }
.decor-element-yellow .line1 { top: 12px; left: 5px; right: 45px; height: 4px; }
.decor-element-yellow .line2 { top: 22px; left: 55px; right: -10px; height: 4px; }
.decor-element-yellow .line3 { top: 40px; left: -25px; right: 65px; height: 4px; }
.decor-element-yellow .line4 { top: 50px; left: 70px; right: -35px; height: 5px; }
.decor-element-yellow .line5 { top: 64px; left: -35px; right: 50px; height: 6px; }
.decor-element-yellow .line6 { top: 82px; left: 55px; right: -30px; height: 6px; }
.decor-element-yellow .line7 { top: 100px; left: -10px; right: 55px; height: 4px; }
.decor-element-yellow .line8 { top: 110px; left: 65px; right: -5px; height: 4px; }

.decor-element-gray {
  position: relative;
  background: #92b6b6bf;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-gray .line { position: absolute; background: #d0e7efaf; border-radius: 4px; opacity: 0.7; }
.decor-element-gray .line1 { top: 10px; left: 0px; right: 60px; height: 4px; }
.decor-element-gray .line2 { top: 26px; left: 60px; right: -12px; height: 4px; }
.decor-element-gray .line3 { top: 38px; left: -28px; right: 38px; height: 5px; }
.decor-element-gray .line4 { top: 56px; left: 38px; right: -38px; height: 6px; }
.decor-element-gray .line5 { top: 70px; left: -38px; right: 68px; height: 5px; }
.decor-element-gray .line6 { top: 84px; left: 48px; right: -18px; height: 5px; }
.decor-element-gray .line7 { top: 98px; left: -2px; right: 58px; height: 6px; }

/* Масштабирование */
.decor-element-purple,
.decor-element-blue,
.decor-element-red,
.decor-element-yellow,
.decor-element-gray {
  width: 120px;
  height: 120px;
  /* width/height будут переопределяться через style */
}
</style>
