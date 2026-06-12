<template>
  <div class="perf-widget">
    <div class="perf-time">{{ digitalTime }}</div>
    <div class="perf-date">{{ dateStr }}</div>

    <div class="perf-grid">
      <div class="perf-item">
        <div class="perf-label">FPS</div>
        <div class="perf-value" :style="{ color: fpsColor }">{{ fps }}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">内存</div>
        <div class="perf-value">{{ memoryStr }}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">DOM 节点</div>
        <div class="perf-value">{{ domCount }}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">JS 堆</div>
        <div class="perf-value">{{ heapStr }}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">网络</div>
        <div class="perf-value">{{ netType }}</div>
      </div>
      <div class="perf-item">
        <div class="perf-label">CPU 核心</div>
        <div class="perf-value">{{ cpuCores }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";

const now = ref(new Date());
const fps = ref(0);
const domCount = ref(0);
const memoryStr = ref("--");
const heapStr = ref("--");
const netType = ref("--");
const cpuCores = ref(navigator.hardwareConcurrency || "--");

let timeTimer: ReturnType<typeof setInterval> | null = null;
let fpsTimer: ReturnType<typeof setInterval> | null = null;
let rafId = 0;
let frameCount = 0;
let lastFpsTime = performance.now();

function tickFps() {
  frameCount++;
  const now = performance.now();
  if (now - lastFpsTime >= 1000) {
    fps.value = Math.round(frameCount * 1000 / (now - lastFpsTime));
    frameCount = 0;
    lastFpsTime = now;
  }
  rafId = requestAnimationFrame(tickFps);
}

function updateMem() {
  const m = (performance as any).memory;
  if (m) {
    const toMB = (b: number) => (b / 1048576).toFixed(1) + " MB";
    memoryStr.value = toMB(m.usedJSHeapSize);
    heapStr.value = toMB(m.totalJSHeapSize);
  }
  domCount.value = document.getElementsByTagName("*").length;
}

function updateNet() {
  const c = (navigator as any).connection;
  if (c) {
    netType.value = `${c.effectiveType || "--"} ${c.downlink || "?"} Mbps`;
  }
}

function pad(n: number) { return n.toString().padStart(2, "0"); }

const digitalTime = computed(() => {
  const d = now.value;
  return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
});

const dateStr = computed(() => {
  const d = now.value;
  const weekdays = ["日", "一", "二", "三", "四", "五", "六"];
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 星期${weekdays[d.getDay()]}`;
});

const fpsColor = computed(() => {
  if (fps.value >= 55) return "#67c23a";
  if (fps.value >= 30) return "#e6a23c";
  return "#f56c6c";
});

onMounted(() => {
  timeTimer = setInterval(() => { now.value = new Date(); }, 1000);
  fpsTimer = setInterval(() => { updateMem(); updateNet(); }, 2000);
  rafId = requestAnimationFrame(tickFps);
  updateMem();
  updateNet();
});

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer);
  if (fpsTimer) clearInterval(fpsTimer);
  cancelAnimationFrame(rafId);
});
</script>

<style scoped>
.perf-widget {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}
.perf-time {
  font-size: 24px;
  font-weight: 700;
  font-family: "Courier New", monospace;
  letter-spacing: 2px;
  color: var(--el-text-color-primary, #303133);
}
.perf-date {
  font-size: 13px;
  color: var(--el-text-color-secondary, #909399);
  margin-bottom: 4px;
}
.perf-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  width: 100%;
}
.perf-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 4px;
  border-radius: 8px;
  background: var(--el-fill-color-lighter, #f5f5f5);
}
.perf-label {
  font-size: 12px;
  color: var(--el-text-color-secondary, #909399);
  margin-bottom: 2px;
}
.perf-value {
  font-size: 18px;
  font-weight: 700;
  font-family: "Courier New", monospace;
  color: var(--el-text-color-primary, #303133);
}
</style>