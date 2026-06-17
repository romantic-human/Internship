<template>
  <div class="dashboard">
    <!-- 顶部欢迎区 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>
            <span class="greeting">{{ greetingText }}</span>
            <span class="name">，{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</span>
          </h1>
          <p class="welcome-desc">这是您的企业智能分析平台概览</p>
        </div>
        <div class="welcome-time">
          <div class="time-display">
            <span class="time">{{ currentTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 核心指标 -->
    <div class="metrics-grid">
      <div
        v-for="(card, idx) in statCards"
        :key="card.label"
        class="metric-card"
        :style="{ '--accent': card.color, '--delay': `${idx * 0.05}s` }"
      >
        <div class="metric-icon">
          <el-icon :size="20"><component :is="card.icon" /></el-icon>
        </div>
        <div class="metric-info">
          <span class="metric-value">{{ card.count }}</span>
          <span class="metric-label">{{ card.label }}</span>
        </div>
      </div>
    </div>

    <!-- 图表区 -->
    <div class="charts-grid">
      <!-- 操作日志 -->
      <div class="chart-card log-card">
        <div class="card-header">
          <div>
            <h3>操作日志</h3>
            <p>实时监控系统操作</p>
          </div>
          <div class="log-badges">
            <span class="badge today">{{ stats.log_today }} 今日</span>
            <span class="badge week">{{ stats.log_week }} 本周</span>
          </div>
        </div>
        <div class="card-body">
          <el-table :data="stats.recent_logs" stripe size="small" max-height="300">
            <template #empty>
              <div class="empty-state">暂无日志记录</div>
            </template>
            <el-table-column prop="username" label="用户" width="80" />
            <el-table-column prop="module" label="模块" width="80" />
            <el-table-column prop="operation" label="操作" width="100" />
            <el-table-column prop="ip" label="IP" width="120" />
            <el-table-column prop="execution_time" label="耗时" width="70" align="center">
              <template #default="{ row }">
                <span :class="{ slow: row.execution_time > 500 }">{{ row.execution_time }}ms</span>
              </template>
            </el-table-column>
            <el-table-column label="时间" min-width="150">
              <template #default="{ row }">
                {{ row.create_time ? formatDate(row.create_time, 'YYYY-MM-DD HH:mm:ss') : '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 部门分布 -->
      <div class="chart-card">
        <div class="card-header">
          <div>
            <h3>部门分布</h3>
            <p>人员分布概览</p>
          </div>
        </div>
        <div class="card-body">
          <div ref="pieChartRef" class="chart-area" />
        </div>
      </div>

      <!-- 登录趋势 -->
      <div class="chart-card">
        <div class="card-header">
          <div>
            <h3>登录趋势</h3>
            <p>近 7 日活跃度</p>
          </div>
        </div>
        <div class="card-body">
          <div ref="lineChartRef" class="chart-area small" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from "vue";
import { useAuthStore } from "@/store/auth";
import { useAppStore } from "@/store/app";
import { getDashboardStats, type DashboardStats } from "@/api/dashboard";
import { User, Menu as MenuIcon, Key, OfficeBuilding, Document, Setting, Timer, Reading, Bell } from "@element-plus/icons-vue";
import * as echarts from "echarts";
import { formatDate } from "@/utils/format";

const authStore = useAuthStore();
const appStore = useAppStore();
const isDark = computed(() => appStore.theme === "dark");
const currentTime = ref("");
let timer: ReturnType<typeof setInterval> | null = null;

const pieChartRef = ref<HTMLDivElement>();
const lineChartRef = ref<HTMLDivElement>();
let pieChart: echarts.ECharts | null = null;
let lineChart: echarts.ECharts | null = null;

const stats = ref<DashboardStats>({
  user_count: 0, role_count: 0, menu_count: 0,
  permission_count: 0, department_count: 0,
  student_count: 0, notification_count: 0,
  today_login_count: 0,
  log_today: 0, log_week: 0, log_month: 0, recent_logs: [],
  dept_distribution: [],
  login_trend: [],
});

const greetingText = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return "夜深了";
  if (hour < 12) return "早上好";
  if (hour < 14) return "中午好";
  if (hour < 18) return "下午好";
  return "晚上好";
});

const statCards = computed(() => [
  { icon: User, count: stats.value.user_count, label: "用户数", color: "#6366f1" },
  { icon: Setting, count: stats.value.role_count, label: "角色数", color: "#8b5cf6" },
  { icon: MenuIcon, count: stats.value.menu_count, label: "菜单数", color: "#a78bfa" },
  { icon: Key, count: stats.value.permission_count, label: "权限数", color: "#c084fc" },
  { icon: OfficeBuilding, count: stats.value.department_count, label: "部门数", color: "#e879f9" },
  { icon: Reading, count: stats.value.student_count, label: "学生数", color: "#f472b6" },
  { icon: Timer, count: stats.value.today_login_count, label: "今日登录", color: "#fb7185" },
  { icon: Bell, count: stats.value.notification_count, label: "未读通知", color: "#fbbf24" },
]);

function updateTime() {
  const now = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  currentTime.value = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

function initCharts() {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value);
    new ResizeObserver(() => pieChart?.resize()).observe(pieChartRef.value);
  }
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value);
    new ResizeObserver(() => lineChart?.resize()).observe(lineChartRef.value);
  }
}

function updateCharts() {
  const textColor = isDark.value ? "#94a3b8" : "#64748b";

  if (pieChart && stats.value.dept_distribution?.length) {
    pieChart.setOption({
      tooltip: { trigger: "item" },
      series: [{
        type: "pie",
        radius: ["45%", "70%"],
        center: ["50%", "50%"],
        itemStyle: { borderRadius: 6, borderColor: isDark.value ? "#1a1728" : "#fff", borderWidth: 3 },
        label: { show: false },
        emphasis: { label: { show: true, formatter: "{b}\n{c}人", color: textColor } },
        data: stats.value.dept_distribution.map((d) => ({ name: d.dept_name, value: d.user_count })),
      }],
    });
  }

  if (lineChart && stats.value.login_trend?.length) {
    lineChart.setOption({
      tooltip: { trigger: "axis" },
      grid: { left: 40, right: 16, top: 16, bottom: 24 },
      xAxis: {
        type: "category",
        data: stats.value.login_trend.map((d) => d.date.slice(5)),
        axisLabel: { color: textColor },
      },
      yAxis: { type: "value", minInterval: 1, axisLabel: { color: textColor } },
      series: [{
        type: "line",
        smooth: true,
        data: stats.value.login_trend.map((d) => d.count),
        areaStyle: { opacity: 0.15 },
        lineStyle: { width: 3, color: "#6366f1" },
        itemStyle: { color: "#6366f1" },
      }],
    });
  }
}

async function fetchStats() {
  try {
    stats.value = await getDashboardStats();
    await nextTick();
    updateCharts();
  } catch { /* handled */ }
}

watch(isDark, () => nextTick(() => updateCharts()));

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
  requestAnimationFrame(() => { initCharts(); fetchStats(); });
});

onUnmounted(() => {
  pieChart?.dispose();
  lineChart?.dispose();
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.dashboard {
  padding: 24px;
  min-height: 100vh;
}

/* ── 欢迎区 ──────────────────────────────────────── */
.welcome-section {
  margin-bottom: 24px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-text h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.greeting {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 8px 0 0;
}

.time-display {
  font-family: "JetBrains Mono", monospace;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

/* ── 指标卡片 ──────────────────────────────────────── */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: var(--accent);
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.metric-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

/* ── 图表区 ──────────────────────────────────────── */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
}

.chart-card.log-card {
  grid-column: 1 / -1;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.card-header p {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 4px 0 0;
}

.log-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.badge.today {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.badge.week {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.card-body {
  padding: 20px 24px;
}

.chart-area {
  height: 240px;
}

.chart-area.small {
  height: 180px;
}

.empty-state {
  text-align: center;
  padding: 32px;
  color: var(--text-secondary);
}

.slow {
  color: #ef4444;
  font-weight: 600;
}

/* ── 暗色模式 ──────────────────────────────────────── */
:global(.dark) .metric-card {
  background: var(--card-bg);
  border-color: var(--border-color);
}

:global(.dark) .metric-card:hover {
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

:global(.dark) .chart-card {
  background: var(--card-bg);
  border-color: var(--border-color);
}

:global(.dark) .badge.today {
  background: rgba(99, 102, 241, 0.15);
}

:global(.dark) .badge.week {
  background: rgba(16, 185, 129, 0.15);
}
</style>
