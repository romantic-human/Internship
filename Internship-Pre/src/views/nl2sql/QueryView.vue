<template>
  <div class="page-container">
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card shadow="never">
          <template #header>
            <div class="flex-between">
              <span>数据源</span>
              <el-button type="primary" link size="small" @click="$router.push('/nl2sql/datasource')">管理</el-button>
            </div>
          </template>
          <el-select v-model="selectedDatasource" placeholder="选择数据源" style="width: 100%"
            @change="loadSchema">
            <el-option v-for="ds in dataSources" :key="ds.id" :label="ds.name" :value="ds.id" />
          </el-select>
          <el-divider style="margin: 12px 0" />
          <div v-loading="schemaLoading" style="min-height: 80px">
            <template v-if="schemaTables.length > 0">
              <div v-for="tbl in schemaTables" :key="tbl.table_name" style="margin-bottom: 8px">
                <div class="table-name" @click="tbl._expanded = !tbl._expanded">
                  <el-icon style="margin-right:4px">
                    <component :is="tbl._expanded ? 'CaretBottom' : 'CaretRight'" />
                  </el-icon>
                  {{ tbl.table_name }}
                </div>
                <div v-if="tbl._expanded" style="padding-left: 24px; font-size: 12px; color: #909399">
                  <div v-for="col in tbl.columns" :key="col.name" style="margin: 2px 0">
                    <span style="color:#409eff">{{ col.name }}</span>
                    <span style="color:#909399; margin-left: 4px">{{ col.type }}</span>
                  </div>
                </div>
              </div>
            </template>
            <el-empty v-else description="请选择数据源" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <el-col :span="18">
        <el-card shadow="never">
          <template #header>
            <span>自然语言查询</span>
          </template>
          <el-input
            v-model="question"
            type="textarea"
            :rows="3"
            placeholder="请输入自然语言问题，如：查询最近10个订单"
            @keydown.enter.prevent="handleQuery"
          />
          <div style="margin-top: 12px">
            <el-button type="primary" :loading="querying" :disabled="!selectedDatasource || !question.trim()"
              @click="handleQuery">
              {{ querying ? '查询中...' : '执行查询' }}
            </el-button>
            <el-button :disabled="!resultData" @click="handleExport">导出结果</el-button>
          </div>

          <el-divider v-if="resultData" />
          <div v-if="resultData" v-loading="querying">
            <div style="margin-bottom: 8px; font-size: 13px; color: #909399">
              <el-tag size="small" type="success" style="margin-right: 8px">
                耗时 {{ resultData.execution_time.toFixed(2) }}s
              </el-tag>
              <el-tag size="small">
                返回 {{ resultData.row_count }} 行
              </el-tag>
            </div>
            <el-input v-model="resultData.sql" type="textarea" :rows="2" readonly
              style="margin-bottom: 12px; font-family: monospace; font-size: 13px" />
            <div style="max-height: 480px; overflow: auto">
              <el-table :data="resultRows" :columns="resultColumns" stripe border
                height="400" size="small">
                <template #empty><el-empty description="无结果" :image-size="50" /></template>
              </el-table>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { CaretRight, CaretBottom } from "@element-plus/icons-vue";
import {
  getDataSourceList, getDataSourceTables, executeQuery,
  type DataSource, type TableMeta, type QueryResult,
} from "@/api/nl2sql";
import * as XLSX from "xlsx";

const route = useRoute();
const dataSources = ref<DataSource[]>([]);
const selectedDatasource = ref<number | null>(null);
const question = ref("");
const querying = ref(false);
const schemaLoading = ref(false);
const schemaTables = ref<(TableMeta & { _expanded?: boolean })[]>([]);
const resultData = ref<QueryResult | null>(null);

const resultRows = computed(() => {
  if (!resultData.value) return [];
  return resultData.value.rows.map((row: any[]) => {
    const obj: Record<string, any> = {};
    resultData.value!.columns.forEach((col: string, i: number) => { obj[col] = row[i]; });
    return obj;
  });
});

const resultColumns = computed(() => {
  if (!resultData.value) return [];
  return resultData.value.columns.map((col: string) => ({ prop: col, label: col, minWidth: 120, showOverflowTooltip: true }));
});

async function loadDataSources() {
  try {
    const res = await getDataSourceList({ page: 1, pageSize: 200, status: 1 });
    dataSources.value = res.records;
    if (route.query.datasource_id) {
      selectedDatasource.value = Number(route.query.datasource_id);
      if (route.query.question) question.value = decodeURIComponent(route.query.question as string);
      loadSchema();
    }
  } catch { /* handled */ }
}

async function loadSchema() {
  if (!selectedDatasource.value) return;
  schemaLoading.value = true;
  try {
    const res = await getDataSourceTables(selectedDatasource.value);
    schemaTables.value = res.tables.map((t) => ({ ...t, _expanded: false }));
  } catch { /* handled */ }
  finally { schemaLoading.value = false; }
}

async function handleQuery() {
  if (!selectedDatasource.value || !question.value.trim()) return;
  querying.value = true;
  try {
    const res = await executeQuery(selectedDatasource.value, question.value.trim());
    resultData.value = res;
  } catch {
    resultData.value = null;
  }
  finally { querying.value = false; }
}

function handleExport() {
  if (!resultData.value || resultData.value.rows.length === 0) {
    ElMessage.warning("没有数据可导出");
    return;
  }
  const ws = XLSX.utils.json_to_sheet(resultRows.value);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "查询结果");
  const now = new Date();
  const dateStr = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}`;
  XLSX.writeFile(wb, `查询结果_${dateStr}.xlsx`);
}

onMounted(loadDataSources);
</script>

<style scoped>
.flex-between { display: flex; justify-content: space-between; align-items: center; }
.table-name { cursor: pointer; font-size: 13px; font-weight: 500; color: #303133; display: flex; align-items: center; }
.table-name:hover { color: #409eff; }
</style>
