<template>
  <div class="log-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>操作日志</span>
          <div>
            <el-button @click="fetchList">刷新</el-button>
            <el-button type="danger" @click="handleClear">清空日志</el-button>
          </div>
        </div>
      </template>
      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="用户名"><el-input v-model="filters.username" placeholder="用户名" clearable style="width:140px" /></el-form-item>
        <el-form-item label="模块"><el-input v-model="filters.module" placeholder="模块" clearable style="width:140px" /></el-form-item>
        <el-form-item label="操作类型"><el-input v-model="filters.operation" placeholder="操作类型" clearable style="width:140px" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width:100px">
            <el-option label="成功" :value="1" /><el-option label="失败" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters={};page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="username" label="用户名" width="100" />
        <el-table-column prop="module" label="模块" width="100" />
        <el-table-column prop="operation" label="操作类型" width="120" />
        <el-table-column prop="method" label="方法" width="80" />
        <el-table-column prop="request_url" label="请求URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP" width="130" />
        <el-table-column label="状态" width="70" align="center">
          <template #default="{ row }"><el-tag :type="row.status ? 'success' : 'danger'" size="small">{{ row.status ? "成功" : "失败" }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="execution_time" label="耗时(ms)" width="90" align="center" />
        <el-table-column prop="create_time" label="操作时间" width="170" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @current-change="fetchList" class="mt-3" />
    </el-card>
    <el-dialog v-model="detailVisible" title="日志详情" width="700px">
      <pre class="log-detail">{{ detailData }}</pre>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getLogList, clearLogs, getLogDetail, type LogItem } from "@/api/log";
import { ElMessage, ElMessageBox } from "element-plus";

const loading = ref(false);
const list = ref<LogItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const filters = ref<Record<string, any>>({});
const detailVisible = ref(false);
const detailData = ref("");

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize };
    Object.entries(filters.value).filter(([_, v]) => v !== "" && v !== undefined && v !== null).forEach(([k, v]) => params[k] = v);
    const res = await getLogList(params);
    list.value = res.records;
    total.value = res.total;
  } finally { loading.value = false; }
}
async function handleDetail(row: LogItem) {
  const res = await getLogDetail(row.id);
  detailData.value = JSON.stringify({ 用户名: res.username, 模块: res.module, 操作: res.operation, 方法: res.method, URL: res.request_url, IP: res.ip, 请求参数: res.request_params, 响应结果: res.response_result, 状态: res.status ? "成功" : "失败", 耗时: `${res.execution_time}ms`, 时间: res.create_time }, null, 2);
  detailVisible.value = true;
}
async function handleClear() {
  try {
    await ElMessageBox.confirm("确定清空所有日志？", "提示");
    await clearLogs(); ElMessage.success("日志已清空"); await fetchList();
  } catch { /* cancel */ }
}
onMounted(fetchList);
</script>
<style scoped>
.log-detail { background: #f5f5f5; padding: 12px; border-radius: 4px; max-height: 400px; overflow: auto; font-size: 13px; }
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>