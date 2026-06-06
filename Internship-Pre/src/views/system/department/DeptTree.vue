<template>
  <div class="dept-tree-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>部门管理</span>
          <div>
            <el-input v-model="keyword" placeholder="部门名称" clearable style="width:200px;margin-right:8px" @input="onKeywordChange" />
            <el-button :disabled="selectedIds.length === 0" type="danger" @click="handleBatchDelete">批量删除</el-button>
            <el-button @click="handleExport">导出</el-button>
            <el-button v-permission="'dept:add'" type="primary" @click="handleAdd">新增部门</el-button>
          </div>
        </div>
      </template>
      <el-table
        :data="filteredTree" row-key="id" default-expand-all
        :tree-props="{ children: 'children' }" v-loading="loading"
        @selection-change="(rows: any[]) => selectedIds = rows.map(r => r.id)"
      >
        <el-table-column type="selection" width="45" />
        <el-table-column prop="dept_name" label="部门名称" min-width="200" />
        <el-table-column prop="leader" label="负责人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.status" :active-value="1" :inactive-value="0"
              @change="(val: number) => handleStatusChange(row, val)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'dept:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm v-permission="'dept:delete'" title="确定删除？" @confirm="handleDelete(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <DeptForm v-if="formVisible" :visible="formVisible" :form-data="currentFormData"
      @close="formVisible = false" @success="fetchTree" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { getDepartmentTree, deleteDepartment, updateDepartmentStatus, batchDeleteDepartments, exportDepartments, type DeptItem } from "@/api/department";
import { ElMessage, ElMessageBox } from "element-plus";
import DeptForm from "./DeptForm.vue";

const loading = ref(false);
const treeData = ref<DeptItem[]>([]);
const formVisible = ref(false);
const currentFormData = ref<Partial<DeptItem> | null>(null);
const keyword = ref("");
const selectedIds = ref<number[]>([]);

function filterTree(items: DeptItem[], kw: string): DeptItem[] {
  return items.reduce<DeptItem[]>((acc, item) => {
    const match = !kw || item.dept_name?.includes(kw);
    const children = item.children ? filterTree(item.children, kw) : [];
    if (match || children.length > 0) {
      acc.push({ ...item, children });
    }
    return acc;
  }, []);
}
const filteredTree = computed(() => keyword.value ? filterTree(treeData.value, keyword.value) : treeData.value);

function onKeywordChange() { /* reactivity handles it */ }

async function fetchTree() {
  loading.value = true;
  try { treeData.value = await getDepartmentTree(); } finally { loading.value = false; }
}
function handleAdd() { currentFormData.value = null; formVisible.value = true; }
function handleEdit(row: DeptItem) { currentFormData.value = { ...row }; formVisible.value = true; }
async function handleDelete(row: DeptItem) {
  try { await deleteDepartment(row.id); ElMessage.success("删除成功"); await fetchTree(); } catch { /* handled by interceptor */ }
}
async function handleStatusChange(row: DeptItem, val: number) {
  try { await updateDepartmentStatus(row.id, val); row.status = val; ElMessage.success("状态更新成功"); } catch { /* handled by interceptor */ }
}
async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个部门？`, "提示");
    await batchDeleteDepartments(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchTree();
  } catch { /* cancel or error */ }
}
async function handleExport() {
  try {
    const blob = await exportDepartments() as unknown as Blob;
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `部门列表_${new Date().toISOString().slice(0, 10)}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch { ElMessage.error("导出失败"); }
}
onMounted(fetchTree);
</script>
