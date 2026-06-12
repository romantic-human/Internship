<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="card-header">
        <div class="header-left">
          <el-select v-model="filters.datasource_id" placeholder="按数据源筛选" clearable style="width: 200px" @change="fetchData">
            <el-option v-for="ds in dataSources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
          <el-checkbox v-model="filters.onlyFavorite" label="仅收藏" @change="fetchData" />
        </div>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <template #empty><el-empty description="暂无查询历史" /></template>
        <el-table-column type="index" label="序号" width="60" align="center"
          :index="(i: number) => (currentPage - 1) * pageSize + i + 1" />
        <el-table-column prop="question" label="自然语言问题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="generated_sql" label="生成的SQL" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <el-code style="font-size:12px">{{ row.generated_sql }}</el-code>
          </template>
        </el-table-column>
        <el-table-column prop="datasource_name" label="数据源" width="120" />
        <el-table-column prop="status" label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result_count" label="结果行数" width="80" align="center" />
        <el-table-column prop="execution_time" label="耗时(s)" width="80" align="center">
          <template #default="{ row }">{{ row.execution_time.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="is_favorite" label="收藏" width="70" align="center">
          <template #default="{ row }">
            <el-button link :type="row.is_favorite ? 'warning' : 'info'"
              :icon="row.is_favorite ? 'StarFilled' : 'Star'" @click="handleToggleFavorite(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="查询时间" width="160" />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleReuse(row)">重新查询</el-button>
            <el-button v-permission="'nl2sql:delete'" type="danger" link size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="currentPage=1;fetchData()"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Star, StarFilled } from "@element-plus/icons-vue";
import {
  getQueryHistoryList, deleteQueryHistory, toggleQueryHistoryFavorite,
  getDataSourceList, type QueryHistory, type DataSource,
} from "@/api/nl2sql";

const router = useRouter();
const loading = ref(false);
const tableData = ref<QueryHistory[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const dataSources = ref<DataSource[]>([]);
const filters = reactive({ datasource_id: undefined as number | undefined, onlyFavorite: false });

async function fetchData() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: currentPage.value, pageSize: pageSize.value };
    if (filters.datasource_id) params.datasource_id = filters.datasource_id;
    if (filters.onlyFavorite) params.is_favorite = 1;
    const res = await getQueryHistoryList(params);
    tableData.value = res.records;
    total.value = res.total;
  } catch { /* handled */ }
  finally { loading.value = false; }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("确定删除该记录？", "提示");
    await deleteQueryHistory(id);
    ElMessage.success("删除成功");
    fetchData();
  } catch { /* cancel or error */ }
}

async function handleToggleFavorite(row: QueryHistory) {
  try {
    await toggleQueryHistoryFavorite(row.id);
    row.is_favorite = row.is_favorite ? 0 : 1;
  } catch { /* handled */ }
}

function handleReuse(row: QueryHistory) {
  router.push(`/nl2sql/query?datasource_id=${row.datasource}&question=${encodeURIComponent(row.question)}`);
}

async function loadDataSources() {
  try {
    const res = await getDataSourceList({ page: 1, pageSize: 200 });
    dataSources.value = res.records;
  } catch { /* handled */ }
}

onMounted(() => { loadDataSources(); fetchData(); });
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-left { display: flex; align-items: center; gap: 12px; }
</style>
