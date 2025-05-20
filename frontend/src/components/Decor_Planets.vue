<template>
  <div v-if="planetTypes[type]">
    <div :class="planet.baseClass" :style="{ width: planetSize + 'px', height: planetSize + 'px' }">
      <div
        v-for="(lineStyle, index) in scaledLines"
        :key="index"
        class="line"
        :style="lineStyle"
      ></div>
    </div>
  </div>
  <svg v-else :width="(radius + strokeWidth) * 2" :height="(radius + strokeWidth) * 2">
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

const scaledLines = computed(() => {
  const baseLines = [
    { top: 15, left: -5, right: 50, height: 5 },
    { top: 32, left: 60, right: -10, height: 4 },
    { top: 42, left: -35, right: 45, height: 5 },
    { top: 62, left: 40, right: -45, height: 5 },
    { top: 76, left: -45, right: 65, height: 4 },
    { top: 87, left: 45, right: -30, height: 4 },
    { top: 102, left: 0, right: 55, height: 4 },
  ];

  return baseLines.map(line => {
    const scale = props.size;
    return {
      top: `${line.top * scale}px`,
      left: `${line.left * scale}px`,
      right: `${line.right * scale}px`,
      height: `${line.height * scale}px`,
    };
  });
});
</script>

<style scoped>
.decor-element-purple {
  position: relative;
  background: #63437328;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-purple .line { position: absolute; background: #b974b280; border-radius: 4px; opacity: 0.7; }
.decor-element-purple .line1 { top: 15px; left: -5px; right: 50px; height: 5px; }
.decor-element-purple .line2 { top: 32px; left: 60px; right: -10px; height: 4px; }
.decor-element-purple .line3 { top: 42px; left: -35px; right: 45px; height: 5px; }
.decor-element-purple .line4 { top: 62px; left: 40px; right: -45px; height: 5px; }
.decor-element-purple .line5 { top: 76px; left: -45px; right: 65px; height: 4px; }
.decor-element-purple .line6 { top: 87px; left: 45px; right: -30px; height: 4px; }
.decor-element-purple .line7 { top: 102px; left: 0px; right: 55px; height: 4px; }

.decor-element-blue {
  position: relative;
  background: #639cec28;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-blue .line { position: absolute; background: #afddf180; border-radius: 4px; opacity: 0.7; }
.decor-element_blue .line1 { top: 18px; left: 60px; right: 0px; height: 4px; }
.decor-element_blue .line2 { top: 34px; left: -15px; right: 55px; height: 6px; }
.decor-element_blue .line3 { top: 48px; left: 40px; right: -40px; height: 5px; }
.decor-element_blue .line4 { top: 66px; left: -45px; right: 30px; height: 4px; }
.decor-element_blue .line5 { top: 80px; left: 65px; right: -25px; height: 6px; }
.decor-element_blue .line6 { top: 92px; left: -30px; right: 50px; height: 5px; }
.decor-element_blue .line7 { top: 106px; left: 50px; right: 5px; height: 4px; }

.decor-element-red {
  position: relative;
  background: #f2412e28;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-red .line { position: absolute; background: #f97c7880; border-radius: 4px; opacity: 0.7; }
.decor-element-red .line1 { top: 16px; left: 35px; right: -30px; height: 6px; }
.decor-element-red .line2 { top: 32px; left: -20px; right:  60px; height: 4px; }
.decor-element-red .line3 { top: 48px; left: 45px; right: -20px; height: 5px; }
.decor-element-red .line4 { top: 60px; left: -45px; right:  65px; height: 6px; }
.decor-element-red .line5 { top: 78px; left: 75px; right: -40px; height: 5px; }
.decor-element-red .line6 { top: 88px; left: -20px; right: 55px; height: 6px; }
.decor-element-red .line7 { top: 106px; left: 65px; right: -10px; height: 4px; }

.decor-element-yellow {
  position: relative;
  background: #cc916528;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-yellow .line { position: absolute; background: #f9c56480; border-radius: 4px; opacity: 0.7; }
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
  background: #92b6b628;
  border-radius: 50%;
  margin: 50px;
}
.decor-element-gray .line { position: absolute; background: #d0e7ef80; border-radius: 4px; opacity: 0.7; }
.decor-element-gray .line1 { top: 10px; left: 0px; right: 60px; height: 4px; }
.decor-element-gray .line2 { top: 26px; left: 60px; right: -12px; height: 4px; }
.decor-element-gray .line3 { top: 38px; left: -28px; right: 38px; height: 5px; }
.decor-element-gray .line4 { top: 56px; left: 38px; right: -38px; height: 6px; }
.decor-element-gray .line5 { top: 70px; left: -38px; right: 68px; height: 5px; }
.decor-element-gray .line6 { top: 84px; left: 48px; right: -18px; height: 5px; }
.decor-element-gray .line7 { top: 98px; left: -2px; right: 58px; height: 6px; }

.decor-element-purple,
.decor-element-blue,
.decor-element-red,
.decor-element-yellow,
.decor-element-gray {
  width: 120px;
  height: 120px;
  overflow: hidden; /* Скрываем выходящие элементы */
  position: relative;
}

.line {
  position: absolute;
  background: inherit;
  border-radius: 4px;
  opacity: 0.7;
  max-width: 100%;
  max-height: 100%;
}

.userhome-main {
  overflow-x: hidden;
}
</style>
