<template>
  <div class="permission-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>权限管理</span>
          <div>
            <el-button type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'permission:add'" type="primary" @click="handleAdd">新增权限</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="权限名称">
          <el-input v-model="filters.permission_name" placeholder="权限名称" clearable style="width:140px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width:100px">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.permission_name='';filters.status=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe @selection-change="onSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="permission_name" label="权限名称" min-width="160" />
        <el-table-column prop="permission_key" label="权限标识" min-width="180" />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val: number) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'permission:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleBindMenu(row)">绑定菜单</el-button>
            <el-popconfirm v-permission="'permission:delete'" title="确定删除？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :page-sizes="[10, 20, 50, 100]" :total="total"
        layout="total, sizes, prev, pager, next, jumper" @current-change="fetchList" @size-change="fetchList" class="mt-3" />
    </el-card>
    <PermissionForm v-if="formVisible" :visible="formVisible" :form-data="currentFormData"
      @close="formVisible = false" @success="fetchList" />

    <!-- 绑定菜单弹窗 -->
    <el-dialog v-model="menuDialogVisible" title="绑定菜单" width="400px">
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
        <el-button type="primary" :loading="menuSaving" @click="handleSaveBindMenu">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, reactive } from "vue";
import {
  getPermissionList,
  deletePermission,
  batchDeletePermissions,
  exportPermissions,
  updatePermissionStatus,
  getPermissionMenus,
  bindPermissionMenus,
  type PermissionItem,
} from "@/api/permission";
import { getMenuTree, type MenuItem } from "@/api/menu";
import { ElMessage, ElMessageBox } from "element-plus";
import type { ElTree } from "element-plus";
import PermissionForm from "./PermissionForm.vue";

const loading = ref(false);
const list = ref<PermissionItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<Partial<PermissionItem> | null>(null);
const selectedIds = ref<number[]>([]);
const filters = reactive({
  permission_name: "",
  status: null as number | null,
});

// 绑定菜单
const menuDialogVisible = ref(false);
const menuTreeData = ref<MenuItem[]>([]);
const menuTreeRef = ref<InstanceType<typeof ElTree>>();
const currentPermissionId = ref(0);
const menuSaving = ref(false);

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize };
    if (filters.permission_name) params.permission_name = filters.permission_name;
    if (filters.status !== null) params.status = filters.status;
    const res = await getPermissionList(params);
    list.value = res.records;
    total.value = res.total;
  } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: PermissionItem) { currentFormData.value = { ...row }; formVisible.value = true; }

async function handleStatusChange(row: PermissionItem, val: number) {
  try {
    await updatePermissionStatus(row.id, val);
    row.status = val;
    ElMessage.success("状态更新成功");
  } catch { /* handled by interceptor */ }
}

function onSelectionChange(rows: PermissionItem[]) {
  selectedIds.value = rows.map(r => r.id);
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条权限？`, "提示");
    await batchDeletePermissions(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchList();
  } catch { /* cancel */ }
}

async function handleExport() {
  const blob = await exportPermissions() as unknown as Blob;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "permissions.csv";
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success("导出成功");
}

async function handleBindMenu(row: PermissionItem) {
  currentPermissionId.value = row.id;
  menuDialogVisible.value = true;
  menuTreeData.value = await getMenuTree();
  nextTick(async () => {
    const menuIds = await getPermissionMenus(row.id);
    menuTreeRef.value?.setCheckedKeys(menuIds);
  });
}

async function handleSaveBindMenu() {
  menuSaving.value = true;
  try {
    const checkedKeys = menuTreeRef.value?.getCheckedKeys(false) as number[];
    await bindPermissionMenus(currentPermissionId.value, checkedKeys);
    ElMessage.success("菜单绑定成功");
    menuDialogVisible.value = false;
  } finally {
    menuSaving.value = false;
  }
}
async function handleDelete(row: PermissionItem) {
  try { await deletePermission(row.id); ElMessage.success("删除成功"); await fetchList(); } catch { /* handled by interceptor */ }
}
onMounted(fetchList);
</script>
<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>
