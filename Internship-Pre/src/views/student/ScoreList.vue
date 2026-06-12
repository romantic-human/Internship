<template>
  <div class="score-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>成绩管理 <el-tag v-if="studentName" type="info" style="margin-left:8px">{{ studentName }}</el-tag></span>
          <div>
            <el-button v-permission="'score:delete'" type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button v-permission="'score:export'" type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'score:import'" @click="handleImport">导入</el-button>
            <el-button v-permission="'score:add'" type="primary" @click="handleAdd">新增成绩</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="课程名称">
          <el-input v-model="filters.course_name" placeholder="课程名称" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="学期">
          <el-input v-model="filters.semester" placeholder="如 2025-2026-1" clearable style="width:150px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.course_name='';filters.semester='';page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="onSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="student_no" label="学号" width="120" />
        <el-table-column prop="student_name" label="姓名" width="100" />
        <el-table-column prop="course_name" label="课程名称" min-width="150" />
        <el-table-column prop="score" label="成绩" width="80" align="center" />
        <el-table-column prop="credit" label="学分" width="70" align="center" />
        <el-table-column prop="semester" label="学期" width="130" />
        <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'score:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <span v-permission="'score:delete'">
              <el-popconfirm title="确定删除该成绩？" @confirm="handleDelete(row)">
                <template #reference><el-button link type="danger">删除</el-button></template>
              </el-popconfirm>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchList"
        @size-change="page=1;fetchList()"
        class="mt-3"
      />
    </el-card>

    <input ref="fileInputRef" type="file" accept=".xlsx,.xls" style="display:none" @change="handleImportChange" />

    <ScoreForm
      v-if="formVisible"
      :visible="formVisible"
      :form-data="currentFormData"
      :student-id="preselectedStudentId"
      @close="formVisible = false"
      @success="fetchList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { useRoute } from "vue-router";
import {
  getScoreList,
  deleteScore,
  batchDeleteScores,
  exportScores,
  importScores,
  type ScoreRecord,
} from "@/api/student";
import { ElMessage, ElMessageBox } from "element-plus";
import ScoreForm from "./ScoreForm.vue";

const route = useRoute();
const studentName = ref((route.query.student_name as string) || "");
const preselectedStudentId = ref<number>(Number(route.query.student_id) || 0);

const loading = ref(false);
const list = ref<ScoreRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const formVisible = ref(false);
const currentFormData = ref<Partial<ScoreRecord> | null>(null);
const selectedIds = ref<number[]>([]);

const filters = reactive({
  course_name: "",
  semester: "",
});
const fileInputRef = ref<HTMLInputElement | null>(null);

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
    if (preselectedStudentId.value) params.student_id = preselectedStudentId.value;
    if (filters.course_name) params.course_name = filters.course_name;
    if (filters.semester) params.semester = filters.semester;
    const res = await getScoreList(params);
    list.value = res.records;
    total.value = res.total;
  } finally {
    loading.value = false;
  }
}

function handleAdd() {
  currentFormData.value = null;
  formVisible.value = true;
}

function handleEdit(row: ScoreRecord) {
  currentFormData.value = { ...row };
  formVisible.value = true;
}

async function handleDelete(row: ScoreRecord) {
  try {
    await deleteScore(row.id);
    ElMessage.success("删除成功");
    await fetchList();
  } catch { /* handled */ }
}

function onSelectionChange(rows: ScoreRecord[]) {
  selectedIds.value = rows.map(r => r.id);
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条成绩？`, "提示");
    await batchDeleteScores(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchList();
  } catch { /* cancel */ }
}

async function handleExport() {
  try {
    const blob = await exportScores() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `成绩列表_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  }
}

async function handleImport() {
  try {
    await ElMessageBox.confirm("请选择 Excel 文件（.xlsx）导入成绩数据。", "导入成绩", {
      confirmButtonText: "选择文件",
      cancelButtonText: "取消",
      type: "info",
    });
    fileInputRef.value?.click();
  } catch { /* cancel */ }
}

async function handleImportChange(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  try {
    await importScores(file);
    ElMessage.success("导入成功");
    await fetchList();
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || "导入失败");
  }
  input.value = "";
}

onMounted(fetchList);
</script>

<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>
