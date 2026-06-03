<template>
  <div class="dashboard">
    <div class="welcome-header">
      <h2>欢迎回来，{{ authStore.userInfo?.nickname || authStore.userInfo?.username }}</h2>
      <p>以下是系统运行概况</p>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="4" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-inner">
            <el-icon :size="32" :color="card.color"><component :is="card.icon" /></el-icon>
            <div class="stat-info">
              <span class="stat-value">{{ card.count }}</span>
              <span class="stat-label">{{ card.label }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="logs-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Clock /></el-icon> 近期操作日志</span>
            </div>
          </template>
          <el-table :data="stats.recent_logs" v-loading="loading" stripe size="small" max-height="360">
            <el-table-column prop="username" label="操作用户" width="100" />
            <el-table-column prop="module" label="模块" width="100" />
            <el-table-column prop="operation" label="操作" width="120" />
            <el-table-column prop="ip" label="IP 地址" width="130" />
            <el-table-column prop="execution_time" label="耗时(ms)" width="90" align="center" />
            <el-table-column prop="create_time" label="操作时间" min-width="160" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "@/store/auth";
import { getDashboardStats, type DashboardStats } from "@/api/dashboard";
import { User, Menu as MenuIcon, Key, OfficeBuilding, Document, Setting, Clock } from "@element-plus/icons-vue";

const authStore = useAuthStore();
const loading = ref(false);

const stats = ref<DashboardStats>({
  user_count: 0, role_count: 0, menu_count: 0,
  permission_count: 0, department_count: 0,
  log_today: 0, log_week: 0, log_month: 0, recent_logs: [],
});

const statCards = computed(() => [
  { icon: User, count: stats.value.user_count, label: "用户数", color: "#409eff" },
  { icon: Setting, count: stats.value.role_count, label: "角色数", color: "#67c23a" },
  { icon: MenuIcon, count: stats.value.menu_count, label: "菜单数", color: "#e6a23c" },
  { icon: Key, count: stats.value.permission_count, label: "权限数", color: "#f56c6c" },
  { icon: OfficeBuilding, count: stats.value.department_count, label: "部门数", color: "#909399" },
  { icon: Document, count: stats.value.log_today, label: "今日日志", color: "#b37feb" },
]);

onMounted(async () => {
  loading.value = true;
  try {
    stats.value = await getDashboardStats();
  } catch { /* handled */ }
  finally { loading.value = false; }
});
</script>

<style scoped>
.dashboard { padding: 16px; }
.welcome-header { margin-bottom: 20px; }
.welcome-header h2 { font-size: 20px; color: #303133; margin: 0 0 4px; }
.welcome-header p { font-size: 14px; color: #909399; margin: 0; }
.stats-row { margin-bottom: 16px; }
.stat-card { cursor: default; }
.stat-inner { display: flex; align-items: center; gap: 12px; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; line-height: 1.2; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }
.card-header { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 15px; }
.logs-row { margin-top: 0; }
</style>