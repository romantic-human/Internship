<template>
  <div class="user-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>用户管理</span>
          <div>
            <el-button type="success" @click="handleExport" :loading="exporting">导出 Excel</el-button>
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="false"
              accept=".xlsx,.xls"
              :on-change="handleImportChange"
            >
              <el-button type="warning" :loading="importing">导入 Excel</el-button>
            </el-upload>
            <el-button @click="showResetRequests = true">重置请求</el-button>
            <el-button type="primary" @click="handleAdd" style="margin-left:8px">新增用户</el-button>
            <el-button
              v-if="selectedRows.length > 0"
              type="danger"
              style="margin-left:8px"
              @click="handleBatchDelete"
            >批量删除 ({{ selectedRows.length }})</el-button>
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
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.username='';filters.status=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="telephone" label="手机号" width="130" />
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
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleResetPwd(row)">重置密码</el-button>
            <el-popconfirm title="确定删除该用户？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchList"
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

    <!-- 密码重置请求管理 -->
    <el-dialog v-model="showResetRequests" title="密码重置请求" width="600px" @open="fetchResetRequests">
      <el-table :data="resetRequests" v-loading="resetLoading" stripe>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="created_at" label="申请时间" width="170" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已重置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" size="small" @click="handleApproveReset(row)">
              审批重置
            </el-button>
            <span v-else style="color:#909399">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
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
  type UserRecord,
} from "@/api/user";
import { ElMessage, ElMessageBox } from "element-plus";
import type { UploadFile } from "element-plus";
import UserForm from "./UserForm.vue";
import { getResetRequests, approveReset, type ResetRequestRecord } from "@/api/user";

const loading = ref(false);
const list = ref<UserRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<Partial<UserRecord> | null>(null);
const exporting = ref(false);
const importing = ref(false);
const selectedRows = ref<UserRecord[]>([]);
const filters = reactive({
  username: "",
  status: null as number | null,
});

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize };
    if (filters.username) params.username = filters.username;
    if (filters.status !== null) params.status = filters.status;
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

async function handleExport() {
  exporting.value = true;
  try {
    const res = await exportUsers();
    const blob = (res as any).data as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "users.xlsx";
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  } finally {
    exporting.value = false;
  }
}

async function handleImportChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return;
  importing.value = true;
  try {
    const res = await importUsers(uploadFile.raw);
    ElMessage.success(`导入完成：成功 ${res.success} 条，跳过 ${res.skipped} 条`);
    await fetchList();
  } catch {
    ElMessage.error("导入失败");
  } finally {
    importing.value = false;
  }
}

function handleSelectionChange(rows: UserRecord[]) {
  selectedRows.value = rows;
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定批量删除选中的 ${selectedRows.value.length} 个用户？`, "批量删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    const ids = selectedRows.value.map((r) => r.id);
    await batchDeleteUsers(ids);
    ElMessage.success("批量删除成功");
    selectedRows.value = [];
    await fetchList();
  } catch {
    // 用户取消
  }
}

// 密码重置请求
const showResetRequests = ref(false);
const resetLoading = ref(false);
const resetRequests = ref<ResetRequestRecord[]>([]);

async function fetchResetRequests() {
  resetLoading.value = true;
  try {
    resetRequests.value = await getResetRequests({ status: "pending" });
  } finally {
    resetLoading.value = false;
  }
}

async function handleApproveReset(row: ResetRequestRecord) {
  try {
    const res = await approveReset({ request_id: row.id });
    ElMessage.success(`已审批，新密码为: ${res.new_password}`);
    await fetchResetRequests();
  } catch {
    // 错误由拦截器处理
  }
}

onMounted(fetchList);
</script>
