<template>
  <div class="config-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <div>
            <el-input v-model="filters.config_name" placeholder="配置名称" clearable style="width:160px;margin-right:8px" />
            <el-input v-model="filters.config_key" placeholder="配置键" clearable style="width:160px;margin-right:8px" />
            <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
            <el-button @click="filters={config_name:'',config_key:''};page=1;fetchList()">重置</el-button>
            <el-button type="primary" @click="handleAdd">新增配置</el-button>
          </div>
        </div>
      </template>
      <el-table :data="list" v-loading="loading" stripe>
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
          <template #default="{ row }"><el-tag :type="row.status ? 'success' : 'danger'" size="small">{{ row.status ? "启用" : "禁用" }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @current-change="fetchList" class="mt-3" />
    </el-card>
    <ConfigForm v-if="formVisible" :visible="formVisible" :form-data="currentFormData"
      @close="formVisible = false" @success="fetchList" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getConfigList, deleteConfig, type ConfigItem } from "@/api/config";
import { ElMessage } from "element-plus";
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

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize };
    if (filters.value.config_name) params.config_name = filters.value.config_name;
    if (filters.value.config_key) params.config_key = filters.value.config_key;
    const res = await getConfigList(params);
    list.value = res.records;
    total.value = res.total;
  } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: ConfigItem) { currentFormData.value = { ...row }; formVisible.value = true; }
async function handleDelete(row: ConfigItem) {
  await deleteConfig(row.id); ElMessage.success("删除成功"); await fetchList();
}
onMounted(fetchList);
</script>
