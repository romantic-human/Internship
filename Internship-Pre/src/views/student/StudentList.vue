<template>
  <div class="student-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>学生管理</span>
          <div>
            <el-button v-permission="'student:delete'" type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button v-permission="'student:export'" type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'student:import'" @click="handleImport">导入</el-button>
            <el-button v-permission="'student:add'" type="primary" @click="handleAdd">新增学生</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="姓名">
          <el-input v-model="filters.name" placeholder="姓名" clearable style="width:130px" />
        </el-form-item>
        <el-form-item label="学号">
          <el-input v-model="filters.student_no" placeholder="学号" clearable style="width:130px" />
        </el-form-item>
        <el-form-item label="班级">
          <el-input v-model="filters.class_name" placeholder="班级" clearable style="width:130px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width:100px">
            <el-option label="休学" :value="0" />
            <el-option label="在读" :value="1" />
            <el-option label="毕业" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.name='';filters.student_no='';filters.class_name='';filters.status=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="onSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="student_no" label="学号" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="70" align="center">
          <template #default="{ row }">{{ genderMap[row.gender] || '未知' }}</template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" min-width="120" />
        <el-table-column prop="major" label="专业" min-width="140" />
        <el-table-column prop="college" label="学院" min-width="130" />
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusMap[row.status] || '未知' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'student:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'student:edit'" link type="primary" @click="handleScore(row)">成绩</el-button>
            <span v-permission="'student:delete'">
              <el-popconfirm title="确定删除该学生？" @confirm="handleDelete(row)">
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

    <StudentForm
      v-if="formVisible"
      :visible="formVisible"
      :form-data="currentFormData"
      @close="formVisible = false"
      @success="fetchList"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { useRouter } from "vue-router";
import {
  getStudentList,
  deleteStudent,
  batchDeleteStudents,
  exportStudents,
  importStudents,
  type StudentRecord,
} from "@/api/student";
import { ElMessage, ElMessageBox } from "element-plus";
import StudentForm from "./StudentForm.vue";

const router = useRouter();
const loading = ref(false);
const list = ref<StudentRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const formVisible = ref(false);
const currentFormData = ref<Partial<StudentRecord> | null>(null);
const selectedIds = ref<number[]>([]);
const fileInputRef = ref<HTMLInputElement | null>(null);

const genderMap: Record<number, string> = { 0: "未知", 1: "男", 2: "女" };
const statusMap: Record<number, string> = { 0: "休学", 1: "在读", 2: "毕业" };
function statusType(s: number) {
  return s === 1 ? "success" : s === 0 ? "warning" : s === 2 ? "info" : "info";
}

const filters = reactive({
  name: "",
  student_no: "",
  class_name: "",
  status: null as number | null,
});

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
    if (filters.name) params.name = filters.name;
    if (filters.student_no) params.student_no = filters.student_no;
    if (filters.class_name) params.class_name = filters.class_name;
    if (filters.status !== null) params.status = filters.status;
    const res = await getStudentList(params);
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

function handleEdit(row: StudentRecord) {
  currentFormData.value = { ...row };
  formVisible.value = true;
}

function handleScore(row: StudentRecord) {
  router.push({ path: "/student/score", query: { student_id: row.id, student_name: row.name } });
}

async function handleDelete(row: StudentRecord) {
  try {
    await deleteStudent(row.id);
    ElMessage.success("删除成功");
    await fetchList();
  } catch { /* handled */ }
}

function onSelectionChange(rows: StudentRecord[]) {
  selectedIds.value = rows.map(r => r.id);
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 名学生？`, "提示");
    await batchDeleteStudents(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchList();
  } catch { /* cancel */ }
}

async function handleExport() {
  try {
    const blob = await exportStudents() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `学生列表_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  }
}

async function handleImport() {
  try {
    await ElMessageBox.confirm("请选择 Excel 文件（.xlsx）导入学生数据。", "导入学生", {
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
    await importStudents(file);
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
