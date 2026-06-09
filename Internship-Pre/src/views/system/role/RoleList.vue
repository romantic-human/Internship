<template>
  <div class="role-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>角色管理</span>
          <div>
            <el-button type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button type="info" @click="handleDownloadTemplate">下载模板</el-button>
            <el-upload :show-file-list="false" accept=".xlsx,.xls" :before-upload="handleImport" style="display:inline-block">
              <el-button type="warning">导入</el-button>
            </el-upload>
            <el-button v-permission="'role:add'" type="primary" @click="handleAdd">新增角色</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="角色名称">
          <el-input v-model="filters.role_name" placeholder="角色名称" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width:100px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.role_name='';filters.status=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="onSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="role_name" label="角色名称" min-width="150" />
        <el-table-column prop="role_key" label="角色标识" width="130" />
        <el-table-column prop="role_sort" label="排序" width="70" align="center" />
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
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'role:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'role:assign'" link type="primary" @click="handleAssignMenu(row)">分配菜单</el-button>
            <el-button v-permission="'role:assign'" link type="primary" @click="handleAssignUser(row)">分配用户</el-button>
            <span v-permission="'role:delete'">
              <el-popconfirm title="确定删除该角色？" @confirm="handleDelete(row)">
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

    <!-- 新增/编辑弹窗 -->
    <RoleForm
      v-if="formVisible"
      :visible="formVisible"
      :form-data="currentFormData"
      @close="formVisible = false"
      @success="fetchList"
    />

    <!-- 分配菜单弹窗 -->
    <el-dialog
      v-model="menuDialogVisible"
      title="分配菜单权限"
      width="400px"
    >
      <el-tree
        ref="menuTreeRef"
        :data="menuTreeData"
        show-checkbox
        node-key="id"
        :props="{ label: 'menu_name', children: 'children' }"
        default-expand-all
        check-strictly
      />
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="menuSaving" @click="handleSaveMenu">保存</el-button>
      </template>
    </el-dialog>

    <!-- 分配用户弹窗 -->
    <el-dialog
      v-model="userDialogVisible"
      title="分配用户"
      width="500px"
    >
      <el-table
        :data="userList"
        ref="userTableRef"
        @selection-change="onUserSelectionChange"
        row-key="id"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
      </el-table>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="userSaving" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, nextTick } from "vue";
import {
  getRoleList,
  deleteRole,
  batchDeleteRoles,
  updateRoleStatus,
  getRoleMenus,
  assignRoleMenus,
  getRoleUsers,
  assignRoleUsers,
  exportRoles,
  importRoles,
  downloadRoleTemplate,
  type RoleRecord,
} from "@/api/role";
import { getMenuTree, type MenuItem } from "@/api/menu";
import { getUserList, type UserRecord } from "@/api/user";
import { ElMessage, ElMessageBox } from "element-plus";
import type { ElTree } from "element-plus";
import RoleForm from "./RoleForm.vue";

const loading = ref(false);
const list = ref<RoleRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const formVisible = ref(false);
const currentFormData = ref<Partial<RoleRecord> | null>(null);
const filters = reactive({
  role_name: "",
  status: null as number | null,
});

// 菜单分配
const menuDialogVisible = ref(false);
const menuTreeData = ref<MenuItem[]>([]);
const menuTreeRef = ref<InstanceType<typeof ElTree>>();
const userTableRef = ref();
const currentRoleId = ref(0);
const menuSaving = ref(false);

// 用户分配
const userDialogVisible = ref(false);
const userList = ref<UserRecord[]>([]);
const selectedUserIds = ref<number[]>([]);
const userSaving = ref(false);

const selectedIds = ref<number[]>([]);

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
    if (filters.role_name) params.role_name = filters.role_name;
    if (filters.status !== null) params.status = filters.status;
    const res = await getRoleList(params);
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

function handleEdit(row: RoleRecord) {
  currentFormData.value = { ...row };
  formVisible.value = true;
}

async function handleDelete(row: RoleRecord) {
  await deleteRole(row.id);
  ElMessage.success("删除成功");
  await fetchList();
}

async function handleStatusChange(row: RoleRecord, val: number) {
  await updateRoleStatus(row.id, val);
  row.status = val;
  ElMessage.success("状态更新成功");
}

// ── 菜单分配 ─────────────────────────────────────────────
async function handleAssignMenu(row: RoleRecord) {
  currentRoleId.value = row.id;
  menuDialogVisible.value = true;
  menuTreeData.value = await getMenuTree();
  const menuIds = await getRoleMenus(row.id);
  await nextTick();
  menuTreeRef.value?.setCheckedKeys(menuIds);
}

async function handleSaveMenu() {
  menuSaving.value = true;
  try {
    const checkedKeys = menuTreeRef.value?.getCheckedKeys(false) as number[];
    await assignRoleMenus(currentRoleId.value, checkedKeys);
    ElMessage.success("菜单权限分配成功");
    menuDialogVisible.value = false;
  } finally {
    menuSaving.value = false;
  }
}

// ── 用户分配 ─────────────────────────────────────────────
async function handleAssignUser(row: RoleRecord) {
  currentRoleId.value = row.id;
  userDialogVisible.value = true;
  const res = await getUserList({ page: 1, pageSize: 999 });
  userList.value = res.records;
  nextTick(async () => {
    const userIds = await getRoleUsers(row.id);
    selectedUserIds.value = userIds;
    // 同步表格选中状态
    const table = userTableRef.value as unknown as { toggleRowSelection(row: UserRecord, selected: boolean): void };
    if (table) {
      userList.value.forEach((u) => {
        table.toggleRowSelection(u, userIds.includes(u.id));
      });
    }
  });
}

async function handleSaveUser() {
  userSaving.value = true;
  try {
    await assignRoleUsers(currentRoleId.value, selectedUserIds.value);
    ElMessage.success("用户分配成功");
    userDialogVisible.value = false;
  } finally {
    userSaving.value = false;
  }
}

function onUserSelectionChange(rows: UserRecord[]) {
  selectedUserIds.value = rows.map((r) => r.id);
}

async function handleExport() {
  try {
    const blob = await exportRoles() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `角色列表_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  }
}

async function handleDownloadTemplate() {
  try {
    const blob = await downloadRoleTemplate() as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "角色导入模板.xlsx";
    a.click();
    window.URL.revokeObjectURL(url);
  } catch {
    ElMessage.error("下载模板失败");
  }
}

async function handleImport(file: File) {
  try {
    await importRoles(file);
    ElMessage.success("导入成功");
    await fetchList();
  } catch { /* handled by interceptor */ }
  return false; // 阻止 el-upload 默认行为
}

function onSelectionChange(rows: RoleRecord[]) {
  selectedIds.value = rows.map(r => r.id);
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个角色？`, "提示");
    await batchDeleteRoles(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchList();
  } catch { /* cancel */ }
}

onMounted(fetchList);
</script>
<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>