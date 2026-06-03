<template>
  <div class="permission-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>权限管理</span>
          <el-button type="primary" @click="handleAdd">新增权限</el-button>
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
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" @click="handleBindMenu(row)">绑定菜单</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
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
    <BindMenuDialog v-if="bindVisible" :visible="bindVisible" :permission-id="bindPermissionId"
      @close="bindVisible = false" @success="fetchList" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getPermissionList, deletePermission } from "@/api/permission";
import { ElMessage } from "element-plus";
import PermissionForm from "./PermissionForm.vue";
import BindMenuDialog from "./BindMenuDialog.vue";

const loading = ref(false);
const list = ref<any[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const formVisible = ref(false);
const currentFormData = ref<any>(null);
const bindVisible = ref(false);
const bindPermissionId = ref(0);

async function fetchList() {
  loading.value = true;
  try {
    const res = await getPermissionList({ page: page.value, pageSize }) as any;
    if (res.records) { list.value = res.records; total.value = res.total; }
    else list.value = res;
  } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: any) { currentFormData.value = { ...row }; formVisible.value = true; }
function handleBindMenu(row: any) { bindPermissionId.value = row.id; bindVisible.value = true; }
async function handleDelete(row: any) {
  try { await deletePermission(row.id); ElMessage.success("删除成功"); await fetchList(); } catch { ElMessage.error("删除失败"); }
}
onMounted(fetchList);
</script>
