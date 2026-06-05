<template>
  <div class="permission-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button v-permission="'permission:add'" type="primary" @click="handleAdd">新增权限</el-button>
        </div>
      </template>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="permission_name" label="权限名称" min-width="160" />
        <el-table-column prop="permission_key" label="权限标识" min-width="180" />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status ? 'success' : 'danger'" size="small">{{ row.status ? "启用" : "禁用" }}</el-tag>
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
      <el-pagination v-if="total > pageSize" v-model:current-page="page" :page-size="pageSize" :total="total"
        layout="total, prev, pager, next" @current-change="fetchList" class="mt-3" />
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
import { ref, onMounted, nextTick } from "vue";
import { getPermissionList, deletePermission, getPermissionMenus, bindPermissionMenus, type PermissionItem } from "@/api/permission";
import { getMenuTree, type MenuItem } from "@/api/menu";
import { ElMessage } from "element-plus";
import type { ElTree } from "element-plus";
import PermissionForm from "./PermissionForm.vue";

const loading = ref(false);
const list = ref<PermissionItem[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<Partial<PermissionItem> | null>(null);

// 绑定菜单
const menuDialogVisible = ref(false);
const menuTreeData = ref<MenuItem[]>([]);
const menuTreeRef = ref<InstanceType<typeof ElTree>>();
const currentPermissionId = ref(0);
const menuSaving = ref(false);

async function fetchList() {
  loading.value = true;
  try {
    const res = await getPermissionList({ page: page.value, pageSize });
    list.value = res.records;
    total.value = res.total;
  } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: PermissionItem) { currentFormData.value = { ...row }; formVisible.value = true; }
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
