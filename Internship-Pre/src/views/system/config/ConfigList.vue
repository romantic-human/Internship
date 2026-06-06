<template>
  <div class="config-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>系统配置</span>
          <div>
            <el-button :disabled="selectedIds.length === 0" type="danger" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'config:add'" type="primary" @click="handleAdd">新增配置</el-button>
          </div>
        </div>
      </template>
      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="配置名称">
          <el-input v-model="filters.config_name" placeholder="配置名称" clearable style="width:160px" />
        </el-form-item>
        <el-form-item label="配置键">
          <el-input v-model="filters.config_key" placeholder="配置键" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters={config_name:'',config_key:''};page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="list" v-loading="loading" stripe @selection-change="(rows: ConfigItem[]) => selectedIds = rows.map(r => r.id)">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="45" />
        <el-table-column prop="config_name" label="配置名称" min-width="160" />
        <el-table-column prop="config_key" label="配置键" min-width="180" />
        <el-table-column prop="config_value" label="配置值" min-width="200" show-overflow-tooltip />
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ TYPE_MAP[row.config_type] ?? "未知" }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.status" :active-value="1" :inactive-value="0" size="small" @change="(val: number) => handleStatusChange(row.id, val)" />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'config:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm v-permission="'config:delete'" title="确定删除？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]" :total="total"
        layout="total, sizes, prev, pager, next, jumper" @current-change="fetchList" @size-change="fetchList" class="mt-3" />
    </el-card>
    <ConfigForm v-if="formVisible" :visible="formVisible" :form-data="currentFormData"
      @close="formVisible = false" @success="fetchList" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getConfigList, deleteConfig, updateConfigStatus, batchDeleteConfigs, exportConfigs, type ConfigItem } from "@/api/config";
import { ElMessage, ElMessageBox } from "element-plus";
import ConfigForm from "./ConfigForm.vue";

const TYPE_MAP: Record<number, string> = { 0: "字符串", 1: "数字", 2: "布尔", 3: "JSON" };
const loading = ref(false);
const list = ref<ConfigItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<Partial<ConfigItem> | null>(null);
const filters = ref({ config_name: "", config_key: "" });
const selectedIds = ref<number[]>([]);

async function fetchList() {
  loading.value = true;
  try {
    const res = await getConfigList({ page: page.value, pageSize });
    list.value = res.records;
    total.value = res.total;
  } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: ConfigItem) { currentFormData.value = { ...row }; formVisible.value = true; }
async function handleDelete(row: ConfigItem) {
  await deleteConfig(row.id); ElMessage.success("删除成功"); await fetchList();
}
async function handleStatusChange(id: number, val: number) {
  await updateConfigStatus(id, val); ElMessage.success("状态更新成功");
}
async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条配置？`, "提示");
    await batchDeleteConfigs(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchList();
  } catch { /* cancel or error */ }
}
async function handleExport() {
  try {
    const blob = await exportConfigs() as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `系统配置_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch { ElMessage.error("导出失败"); }
}
onMounted(fetchList);
</script>
<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>
