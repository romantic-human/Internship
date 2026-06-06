<template>
  <div class="user-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>用户管理</span>
          <div>
            <el-button type="success" @click="handleExport">导出 Excel</el-button>
            <el-upload
              :show-file-list="false"
              accept=".xlsx,.xls"
              :before-upload="handleImport"
              style="display:inline-block;margin:0 8px"
            >
              <el-button type="warning">批量导入用户</el-button>
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
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.username='';filters.status=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" align="center"
          :index="(i:number) => (page - 1) * pageSize + i + 1" />
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
            <el-popconfirm v-permission="'user:delete'" title="确定删除该用户？" @confirm="handleDelete(row)">
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
  type UserRecord,
} from "@/api/user";
import { ElMessage, ElMessageBox } from "element-plus";
import UserForm from "./UserForm.vue";

const loading = ref(false);
const list = ref<UserRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);
const formVisible = ref(false);
const currentFormData = ref<Partial<UserRecord> | null>(null);
const filters = reactive({
  username: "",
  status: null as number | null,
});

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
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

onMounted(fetchList);

async function handleExport() {
  try {
    const blob = await exportUsers() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "users.xlsx";
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch { /* handled by interceptor */ }
}

async function handleImport(file: File) {
  try {
    const res = await importUsers(file);
    ElMessage.success(`导入完成：成功 ${res.success} 条，跳过 ${res.skipped} 条`);
    await fetchList();
  } catch { /* handled by interceptor */ }
  return false; // prevent el-upload default
}
</script>
