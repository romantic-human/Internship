<template>
  <div class="menu-tree-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>菜单管理</span>
          <div>
            <el-button type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'menu:add'" type="primary" @click="handleAdd">新增菜单</el-button>
          </div>
        </div>
      </template>

      <el-form inline class="mb-2">
        <el-form-item label="菜单名称">
          <el-input v-model="searchKey" placeholder="菜单名称" clearable style="width:200px" @clear="fetchTree" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchTree">查询</el-button>
          <el-button @click="searchKey='';fetchTree()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        ref="tableRef"
        :data="treeData"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children' }"
        v-loading="loading"
        stripe
        @selection-change="onSelectionChange"
      >
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" reserve-selection />
        <el-table-column prop="menu_name" label="菜单名称" min-width="200" />
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.icon">
              <component :is="iconMap[row.icon] || MenuIcon" />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="typeTagType(row.menu_type)"
              size="small"
            >
              {{ TYPE_MAP[row.menu_type] ?? "未知" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" min-width="160" />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column prop="permission" label="权限标识" min-width="150" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val: number) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'menu:edit'" link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button v-permission="'menu:add'" link type="primary" @click="handleAddChild(row)">新增子菜单</el-button>
            <span v-permission="'menu:delete'">
              <el-popconfirm title="确定删除该菜单？" @confirm="handleDelete(row)">
                <template #reference>
                  <el-button link type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <MenuForm
      v-if="formVisible"
      :visible="formVisible"
      :form-data="currentFormData"
      :tree-options="flattenForOptions(treeData)"
      @close="formVisible = false"
      @success="fetchTree"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { getMenuTree, deleteMenu, updateMenuStatus, batchDeleteMenus, exportMenus, batchSortMenu, type MenuItem } from "@/api/menu";
import { ElMessage, ElMessageBox } from "element-plus";
import { markRaw, shallowRef, type Component } from "vue";
import * as ElementPlusIcons from "@element-plus/icons-vue";
import MenuForm from "./MenuForm.vue";
import Sortable from "sortablejs";

const iconMap: Record<string, Component> = {};
for (const [key, comp] of Object.entries(ElementPlusIcons)) {
  iconMap[key] = markRaw(comp);
}
const MenuIcon = shallowRef(ElementPlusIcons["Menu"]);
const TYPE_MAP: Record<number, string> = { 0: "目录", 1: "菜单", 2: "按钮" };

const loading = ref(false);
const treeData = ref<MenuItem[]>([]);
const formVisible = ref(false);
const currentFormData = ref<Partial<MenuItem> | null>(null);
const searchKey = ref("");
const selectedIds = ref<number[]>([]);
const tableRef = ref();

function onSelectionChange(rows: MenuItem[]) {
  selectedIds.value = rows.map(r => r.id);
}

function typeTagType(t: number): string {
  return t === 0 ? "" : t === 1 ? "primary" : "warning";
}

function flattenForOptions(items: MenuItem[]): (Partial<MenuItem> & { _level: number })[] {
  const result: (Partial<MenuItem> & { _level: number })[] = [];
  function walk(list: MenuItem[], level: number) {
    for (const item of list) {
      result.push({ ...item, _level: level });
      if (item.children?.length) walk(item.children, level + 1);
    }
  }
  walk(items, 0);
  return result;
}

async function fetchTree() {
  loading.value = true;
  try {
    const params: Record<string, any> = {};
    if (searchKey.value) params.menu_name = searchKey.value;
    treeData.value = await getMenuTree(params);
  } finally {
    loading.value = false;
  }
}

function handleAdd() {
  currentFormData.value = null;
  formVisible.value = true;
}

function handleAddChild(row: MenuItem) {
  currentFormData.value = { parent_id: row.id };
  formVisible.value = true;
}

function handleEdit(row: MenuItem) {
  currentFormData.value = { ...row };
  formVisible.value = true;
}

async function handleDelete(row: MenuItem) {
  try {
    await deleteMenu(row.id);
    ElMessage.success("删除成功");
    await fetchTree();
  } catch { /* handled by interceptor */ }
}

async function handleStatusChange(row: MenuItem, val: number) {
  try {
    await updateMenuStatus(row.id, val);
    row.status = val;
    ElMessage.success("状态更新成功");
  } catch { /* handled by interceptor */ }
}

async function handleBatchDelete() {
  if (!selectedIds.value.length) return;
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个菜单？`, "批量删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
  } catch { return; }
  try {
    await batchDeleteMenus(selectedIds.value);
    ElMessage.success("批量删除成功");
    selectedIds.value = [];
    await fetchTree();
  } catch { /* handled by interceptor */ }
}

async function handleExport() {
  try {
    const blob = await exportMenus() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "menus.xlsx";
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("导出成功");
  } catch { /* handled by interceptor */ }
}

function initDragSort() {
  nextTick(() => {
    const el = tableRef.value?.$el?.querySelector('.el-table__body-wrapper tbody');
    if (!el) return;
    Sortable.create(el, {
      handle: '.el-table__row',
      animation: 150,
      ghostClass: 'sortable-ghost',
      onEnd: async (evt: any) => {
        if (evt.oldIndex === evt.newIndex) return;
        const flatRows = tableRef.value?.data;
        if (!flatRows) return;
        const oldItem = flatRows[evt.oldIndex];
        const newItem = flatRows[evt.newIndex];
        // Only reorder within same parent level
        if (oldItem?.parent_id !== newItem?.parent_id) {
          ElMessage.warning('只能在同一层级内拖拽排序');
          await fetchTree();
          return;
        }
        const siblings = flatRows.filter((r: MenuItem) => r.parent_id === oldItem.parent_id);
        const payload = siblings.map((item: MenuItem, idx: number) => ({
          id: item.id,
          sortOrder: idx,
        }));
        try {
          await batchSortMenu(payload);
          ElMessage.success('排序更新成功');
          await fetchTree();
        } catch { /* handled by interceptor */ }
      },
    });
  });
}

onMounted(() => {
  fetchTree().then(initDragSort);
});
</script>
<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
</style>