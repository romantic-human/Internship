<template>
  <div class="user-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>用户管理</span>
          <div>
            <el-button
              :disabled="selectedRows.length === 0"
              type="danger"
              @click="handleBatchDelete"
            >批量删除{{ selectedRows.length ? ` (${selectedRows.length})` : '' }}</el-button>
            <el-button type="success" @click="handleExport" :loading="exporting">导出用户</el-button>
            <el-button type="info" @click="handleDownloadTemplate">下载模板</el-button>
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="false"
              accept=".xlsx,.xls"
              :on-change="handleImportChange"
              style="display:inline-block"
            >
              <el-button type="warning" :loading="importing">批量导入用户</el-button>
            </el-upload>
            <el-button v-permission="'user:add'" type="primary" @click="handleAdd">新增用户</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="用户名">
          <el-input v-model="filters.username" placeholder="用户名" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width:100px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-tree-select
            v-model="filters.department_id"
            :data="deptOptions"
            :props="{ label: 'dept_name', children: 'children', value: 'id' }"
            placeholder="全部部门"
            check-strictly
            clearable
            filterable
            style="width:160px"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.role_id" placeholder="全部角色" clearable style="width:140px">
            <el-option v-for="r in roleOptions" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="注册时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            style="width:220px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="handleSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="index" label="序号" width="60" align="center"
          :index="(i: number) => (page - 1) * pageSize + i + 1" />
        <el-table-column type="selection" width="45" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="telephone" label="手机号" width="130" />
        <el-table-column prop="department_name" label="部门" width="120">
          <template #default="{ row }">
            {{ row.department_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="role_name" label="角色" min-width="140">
          <template #default="{ row }">
            <template v-if="row.role_name">
              <el-tag v-for="name in row.role_name.split('、')" :key="name" size="small"
                style="margin-right:4px">{{ name }}</el-tag>
            </template>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val:number) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="170">
          <template #default="{ row }">
            {{ row.last_login || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'user:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleResetPwd(row)">重置密码</el-button>
            <el-popconfirm v-if="authStore.hasPermission('user:delete')" title="确定删除该用户？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchList"
        @size-change="page=1;fetchList()"
        class="mt-3"
      />
    </el-card>

    <UserForm
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
import {
  getUserList,
  deleteUser,
  updateUserStatus,
  resetPassword,
  exportUsers,
  importUsers,
  batchDeleteUsers,
  downloadUserTemplate,
  type UserRecord,
} from "@/api/user";
import { getDepartmentTree, type DeptItem } from "@/api/department";
import { getAllRoles, type RoleRecord } from "@/api/role";
import { ElMessage, ElMessageBox } from "element-plus";
import type { UploadFile } from "element-plus";
import { useAuthStore } from "@/store/auth";
import UserForm from "./UserForm.vue";

const authStore = useAuthStore();

const loading = ref(false);
const list = ref<UserRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);
const formVisible = ref(false);
const currentFormData = ref<Partial<UserRecord> | null>(null);
const exporting = ref(false);
const importing = ref(false);
const selectedRows = ref<UserRecord[]>([]);
const deptOptions = ref<DeptItem[]>([]);
const roleOptions = ref<RoleRecord[]>([]);
const dateRange = ref<[string, string] | null>(null);
const filters = reactive({
  username: "",
  status: null as number | null,
  department_id: null as number | null,
  role_id: null as number | null,
});

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
    if (filters.username) params.username = filters.username;
    if (filters.status !== null) params.status = filters.status;
    if (filters.department_id) params.department_id = filters.department_id;
    if (filters.role_id) params.role_id = filters.role_id;
    if (dateRange.value) {
      params.start_date = dateRange.value[0];
      params.end_date = dateRange.value[1];
    }
    const res = await getUserList(params);
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

function handleEdit(row: UserRecord) {
  currentFormData.value = { ...row };
  formVisible.value = true;
}

async function handleDelete(row: UserRecord) {
  await deleteUser(row.id);
  ElMessage.success("删除成功");
  await fetchList();
}

async function handleStatusChange(row: UserRecord, val: number) {
  await updateUserStatus(row.id, val);
  row.status = val;
  ElMessage.success("状态更新成功");
}

function handleResetPwd(row: UserRecord) {
  ElMessageBox.confirm(`确定将用户「${row.username}」的密码重置为 123456？`, "重置密码", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(async () => {
    await resetPassword({ userId: row.id });
    ElMessage.success("密码已重置为 123456");
  }).catch(() => {});
}

function handleSelectionChange(rows: UserRecord[]) {
  selectedRows.value = rows;
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 个用户？`, "批量删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
  } catch {
    return;
  }
  const ids = selectedRows.value.map((r) => r.id);
  await batchDeleteUsers(ids);
  ElMessage.success("批量删除成功");
  selectedRows.value = [];
  await fetchList();
}

async function handleExport() {
  exporting.value = true;
  try {
    const blob = await exportUsers() as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `用户列表_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } finally {
    exporting.value = false;
  }
}

async function handleDownloadTemplate() {
  try {
    const blob = await downloadUserTemplate() as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "用户导入模板.xlsx";
    a.click();
    window.URL.revokeObjectURL(url);
  } catch {
    ElMessage.error("下载模板失败");
  }
}

async function handleImportChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return;
  importing.value = true;
  try {
    await importUsers(uploadFile.raw);
    ElMessage.success("导入成功");
    await fetchList();
  } catch {
    ElMessage.error("导入失败");
  } finally {
    importing.value = false;
  }
}

function resetFilters() {
  filters.username = '';
  filters.status = null;
  filters.department_id = null;
  filters.role_id = null;
  dateRange.value = null;
  page.value = 1;
  fetchList();
}

async function loadFilterOptions() {
  try {
    deptOptions.value = await getDepartmentTree();
    roleOptions.value = await getAllRoles();
  } catch { /* ignore */ }
}

onMounted(() => {
  loadFilterOptions();
  fetchList();
});
</script>
<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>
