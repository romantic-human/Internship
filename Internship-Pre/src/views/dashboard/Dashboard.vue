<template>
  <div class="dashboard">
    <div class="welcome-header">
      <div>
        <h2>欢迎回来，{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</h2>
        <p class="time-text">{{ currentTime }}</p>
      </div>
      <el-button :icon="Refresh" :loading="loading" @click="fetchStats">刷新数据</el-button>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6" :md="4" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card" :body-style="{ padding: '16px' }" :style="{ '--card-color': card.color }">
          <div class="stat-inner">
            <div class="stat-icon">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ card.count }}</span>
              <span class="stat-label">{{ card.label }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> 近期操作日志</span>
              <span class="log-stats-badge">
                <el-tag size="small" type="primary">今日 {{ stats.log_today }}</el-tag>
                <el-tag size="small" type="success">本周 {{ stats.log_week }}</el-tag>
                <el-tag size="small" type="warning">本月 {{ stats.log_month }}</el-tag>
              </span>
            </div>
          </template>
          <el-table :data="stats.recent_logs" v-loading="loading" stripe size="small" max-height="320">
            <el-table-column prop="username" label="用户" width="80" />
            <el-table-column prop="module" label="模块" width="80" />
            <el-table-column prop="operation" label="操作" width="100" />
            <el-table-column prop="ip" label="IP" width="120" />
            <el-table-column prop="execution_time" label="耗时" width="70" align="center">
              <template #default="{ row }">
                <span>{{ row.execution_time }}ms</span>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="时间" min-width="150" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" style="margin-bottom:12px">
          <template #header>
            <div class="card-header"><el-icon><MenuIcon /></el-icon> 用户部门分布</div>
          </template>
          <div ref="pieChartRef" style="height:280px" />
        </el-card>
        <el-card shadow="hover">
          <template #header>
            <div class="card-header"><el-icon><Timer /></el-icon> 近7日登录趋势</div>
          </template>
          <div ref="lineChartRef" style="height:200px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from "vue";
import { useAuthStore } from "@/store/auth";
import { getDashboardStats, type DashboardStats } from "@/api/dashboard";
import { User, Menu as MenuIcon, Key, OfficeBuilding, Document, Setting, Refresh, Timer } from "@element-plus/icons-vue";
import * as echarts from "echarts";

const authStore = useAuthStore();
const loading = ref(false);
const currentTime = ref("");
let timer: ReturnType<typeof setInterval> | null = null;

const pieChartRef = ref<HTMLDivElement>();
const lineChartRef = ref<HTMLDivElement>();
let pieChart: echarts.ECharts | null = null;
let lineChart: echarts.ECharts | null = null;
let pieResize: ResizeObserver | null = null;
let lineResize: ResizeObserver | null = null;

const stats = ref<DashboardStats>({
  user_count: 0, role_count: 0, menu_count: 0,
  permission_count: 0, department_count: 0,
  today_login_count: 0,
  log_today: 0, log_week: 0, log_month: 0, recent_logs: [],
  dept_distribution: [],
  login_trend: [],
});

const statCards = computed(() => [
  { icon: User, count: stats.value.user_count, label: "用户数", color: "#409eff" },
  { icon: Setting, count: stats.value.role_count, label: "角色数", color: "#67c23a" },
  { icon: MenuIcon, count: stats.value.menu_count, label: "菜单数", color: "#e6a23c" },
  { icon: Key, count: stats.value.permission_count, label: "权限数", color: "#f56c6c" },
  { icon: OfficeBuilding, count: stats.value.department_count, label: "部门数", color: "#909399" },
  { icon: Timer, count: stats.value.today_login_count, label: "今日登录", color: "#36cfc9" },
  { icon: Document, count: stats.value.log_today, label: "今日日志", color: "#b37feb" },
]);

function updateTime() {
  const now = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
}

function initCharts() {
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value);
    pieResize = new ResizeObserver(() => pieChart?.resize());
    pieResize.observe(pieChartRef.value);
  }
  if (lineChartRef.value) {
    lineChart = echarts.init(lineChartRef.value);
    lineResize = new ResizeObserver(() => lineChart?.resize());
    lineResize.observe(lineChartRef.value);
  }
}

function updateCharts() {
  if (pieChart && stats.value.dept_distribution?.length) {
    pieChart.setOption({
      tooltip: { trigger: "item" },
      series: [{
        type: "pie",
        radius: ["40%", "65%"],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 4, borderColor: "#fff", borderWidth: 2 },
        label: { show: true, formatter: "{b}: {c}" },
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
      },
      yAxis: { type: "value", minInterval: 1 },
      series: [{
        type: "line",
        smooth: true,
        data: stats.value.login_trend.map((d) => d.count),
        areaStyle: { opacity: 0.15 },
        lineStyle: { width: 2 },
        itemStyle: { color: "#409eff" },
      }],
    });
  }
}

async function fetchStats() {
  loading.value = true;
  try {
    stats.value = await getDashboardStats();
    await nextTick();
    updateCharts();
  } catch { /* handled */ }
  finally { loading.value = false; }
}

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
  requestAnimationFrame(() => {
    initCharts();
    fetchStats();
  });
});

onUnmounted(() => {
  pieResize?.disconnect();
  lineResize?.disconnect();
  pieChart?.dispose();
  lineChart?.dispose();
  if (timer) clearInterval(timer);
});
</script>

<style>
.dashboard { padding: 16px; }
.welcome-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.welcome-header h2 { font-size: 20px; color: var(--text-primary); margin: 0 0 2px; }
.time-text { font-size: 13px; color: var(--text-secondary); margin: 0; font-family: monospace; }
.stats-row { margin-bottom: 16px; }
.stat-card { cursor: default; transition: transform 0.2s, box-shadow 0.2s; border-top: 3px solid var(--card-color); }
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px var(--shadow-color); }
.stat-inner { display: flex; align-items: center; gap: 12px; }
.stat-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #fff; background: var(--card-color); }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }
.card-header { display: flex; align-items: center; justify-content: space-between; gap: 6px; font-weight: 600; font-size: 15px; }
.log-stats-badge { display: flex; gap: 6px; }
.logs-row { margin-top: 0; }
.log-stats { display: flex; flex-direction: column; gap: 16px; }
.log-stat-item { display: flex; flex-direction: column; gap: 4px; }
.log-stat-label { font-size: 14px; color: #606266; }

.dark .welcome-header h2 { color: #e0e2e8; }
.dark .stat-value { color: #e0e2e8; }

</style>
