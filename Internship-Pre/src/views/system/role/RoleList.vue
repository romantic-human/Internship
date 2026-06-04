<template>
  <div class="role-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>角色管理</span>
          <el-button type="primary" @click="handleAdd">新增角色</el-button>
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

      <el-table :data="list" v-loading="loading" stripe>
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
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleAssignMenu(row)">分配菜单</el-button>
            <el-button link type="primary" @click="handleAssignUser(row)">分配用户</el-button>
            <el-popconfirm title="确定删除该角色？" @confirm="handleDelete(row)">
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
        @selection-change="selectedUserIds = $event.map((r:any)=>r.id)"
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
  updateRoleStatus,
  getRoleMenus,
  assignRoleMenus,
  getRoleUsers,
  assignRoleUsers,
  type RoleRecord,
} from "@/api/role";
import { getMenuTree } from "@/api/menu";
import { getUserList } from "@/api/user";
import { ElMessage } from "element-plus";
import type { ElTree } from "element-plus";
import RoleForm from "./RoleForm.vue";

const loading = ref(false);
const list = ref<RoleRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<Partial<RoleRecord> | null>(null);
const filters = reactive({
  role_name: "",
  status: null as number | null,
});

// 菜单分配
const menuDialogVisible = ref(false);
const menuTreeData = ref<any[]>([]);
const menuTreeRef = ref<InstanceType<typeof ElTree>>();
const currentRoleId = ref(0);
const menuSaving = ref(false);

// 用户分配
const userDialogVisible = ref(false);
const userList = ref<any[]>([]);
const selectedUserIds = ref<number[]>([]);
const userSaving = ref(false);

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize };
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
  nextTick(async () => {
    const menuIds = await getRoleMenus(row.id);
    menuTreeRef.value?.setCheckedKeys(menuIds);
  });
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

onMounted(fetchList);
</script>