<template>
  <div class="menu-tree-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>菜单管理</span>
          <div>
            <el-button v-if="sortDirty" type="success" :loading="sortSaving" @click="handleSaveSort">
              <el-icon><Check /></el-icon>保存排序
            </el-button>
            <el-button v-if="sortDirty" @click="handleCancelSort">撤销</el-button>
            <el-button v-permission="'menu:delete'" type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button @click="handleDownloadTemplate">下载模板</el-button>
            <el-button type="warning" @click="importDialogVisible = true">导入</el-button>
            <el-button v-permission="'menu:add'" type="primary" @click="handleAdd">新增菜单</el-button>
          </div>
        </div>
      </template>

      <el-alert
        v-if="sortDirty"
        title="排序已变更，点击右上角「保存排序」提交更改，或「撤销」恢复原序"
        type="warning"
        show-icon
        :closable="false"
        style="margin-bottom: 16px; border-radius: 8px;"
      />

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
        :tree-props="{ children: 'children' }"
        v-loading="loading"
        stripe
        @selection-change="onSelectionChange"
      >
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" reserve-selection />
        <el-table-column label="" width="50" align="center">
          <template #default>
            <el-icon class="drag-handle" style="cursor:grab;font-size:16px;color:#909399"><Rank /></el-icon>
          </template>
        </el-table-column>
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
        <el-table-column label="排序" width="100" align="center">
          <template #default="{ row }">
            <div style="display:flex;align-items:center;justify-content:center;gap:4px">
              <el-button link :disabled="!canMoveUp(row)" @click="handleMoveUp(row)">
                <el-icon><Top /></el-icon>
              </el-button>
              <span style="min-width:20px;text-align:center;font-size:12px;color:#909399">{{ row.sort_order }}</span>
              <el-button link :disabled="!canMoveDown(row)" @click="handleMoveDown(row)">
                <el-icon><Bottom /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
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

    <el-dialog v-model="importDialogVisible" title="导入菜单" width="500px">
      <el-upload drag :auto-upload="false" accept=".xlsx,.xls" :limit="1" :on-change="handleImportFile" :file-list="importFileList">
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip><div class="el-upload__tip">仅支持 .xlsx / .xls 文件</div></template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="handleImport">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { getMenuTree, deleteMenu, updateMenuStatus, batchDeleteMenus, exportMenus, batchSortMenu, importMenus, downloadMenuTemplate, type MenuItem } from "@/api/menu";
import { ElMessage, ElMessageBox } from "element-plus";
import { markRaw, shallowRef, type Component } from "vue";
import * as ElementPlusIcons from "@element-plus/icons-vue";
import { Check, Rank, Top, Bottom } from "@element-plus/icons-vue";
import MenuForm from "./MenuForm.vue";
import { useAuthStore } from "@/store/auth";

const authStore = useAuthStore();

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
const sortDirty = ref(false);
const sortSaving = ref(false);
const pendingSortPayload = ref<{ id: number; sortOrder: number }[]>([]);
const originalTreeJson = ref('');

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
    originalTreeJson.value = JSON.stringify(treeData.value);
    sortDirty.value = false;
    pendingSortPayload.value = [];
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

/** 在嵌套树中找到 item 所在的兄弟数组和索引 */
function findInTree(id: number, list: MenuItem[], parent: MenuItem[] = list): { siblings: MenuItem[]; index: number } | null {
  for (let i = 0; i < list.length; i++) {
    if (list[i].id === id) return { siblings: parent, index: i };
    if (list[i].children?.length) {
      const found = findInTree(id, list[i].children!, list[i].children!);
      if (found) return found;
    }
  }
  return null;
}

/** 上移 */
function handleMoveUp(row: MenuItem) {
  const loc = findInTree(row.id, treeData.value);
  if (!loc || loc.index <= 0) return;
  const { siblings, index } = loc;
  [siblings[index - 1], siblings[index]] = [siblings[index], siblings[index - 1]];
  treeData.value = [...treeData.value]; // 触发响应式更新
  markSortDirty();
}

/** 下移 */
function handleMoveDown(row: MenuItem) {
  const loc = findInTree(row.id, treeData.value);
  if (!loc || loc.index >= loc.siblings.length - 1) return;
  const { siblings, index } = loc;
  [siblings[index], siblings[index + 1]] = [siblings[index + 1], siblings[index]];
  treeData.value = [...treeData.value]; // 触发响应式更新
  markSortDirty();
}

/** 判断是否可以上移 */
function canMoveUp(row: MenuItem): boolean {
  const loc = findInTree(row.id, treeData.value);
  return !!loc && loc.index > 0;
}

/** 判断是否可以下移 */
function canMoveDown(row: MenuItem): boolean {
  const loc = findInTree(row.id, treeData.value);
  return !!loc && loc.index < loc.siblings.length - 1;
}

/** 标记排序已变更，构建 payload（递归收集所有项） */
function markSortDirty() {
  const payload: { id: number; sortOrder: number }[] = [];
  function collect(items: MenuItem[]) {
    for (let i = 0; i < items.length; i++) {
      payload.push({ id: items[i].id, sortOrder: i });
      if (items[i].children?.length) collect(items[i].children!);
    }
  }
  collect(treeData.value);
  pendingSortPayload.value = payload;
  sortDirty.value = true;
}

function initDragSort() {
  // 排序通过上移/下移按钮实现
}

/** 保存排序 */
async function handleSaveSort() {
  if (!pendingSortPayload.value.length) return;
  sortSaving.value = true;
  try {
    await batchSortMenu(pendingSortPayload.value);
    ElMessage.success('排序保存成功');
    await fetchTree();
    await authStore.refreshMenuTree();
    initDragSort();
  } catch { /* handled */ } finally {
    sortSaving.value = false;
  }
}

/** 撤销排序 */
async function handleCancelSort() {
  await fetchTree();
  initDragSort();
  ElMessage.info('已撤销排序变更');
}

onMounted(() => {
  fetchTree().then(initDragSort);
});

const importDialogVisible = ref(false);
const importLoading = ref(false);
const importFileList = ref<any[]>([]);

function handleImportFile(file: any) {
  importFileList.value = [file];
}

async function handleImport() {
  if (!importFileList.value.length) { ElMessage.warning("请先选择文件"); return; }
  importLoading.value = true;
  try {
    const res = await importMenus(importFileList.value[0].raw);
    ElMessage.success("导入完成: 成功" + res.success + "条, 跳过" + res.skipped + "条");
    importDialogVisible.value = false;
    importFileList.value = [];
    await fetchTree();
  } catch { /* handled */ } finally { importLoading.value = false; }
}

async function handleDownloadTemplate() {
  try {
    const blob = await downloadMenuTemplate() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "menu_template.xlsx"; a.click();
    URL.revokeObjectURL(url);
    ElMessage.success("模板下载成功");
  } catch { /* handled */ }
}
</script>

<style scoped>
/* ── 菜单树层级样式 ── */
:deep(.el-table__row) {
  transition: background-color 0.15s ease;
}

/* 顶层菜单：左侧蓝色竖线 + 加粗 */
:deep(.el-table__row--level-0 td:first-child) {
  border-left: 3px solid var(--el-color-primary, #409eff);
  padding-left: 12px;
}
:deep(.el-table__row--level-0 .cell) {
  font-weight: 600;
  color: var(--el-text-color-primary, #303133);
}

/* 二级菜单：左侧绿色竖线 */
:deep(.el-table__row--level-1 td:first-child) {
  border-left: 3px solid #67c23a;
  padding-left: 12px;
}
:deep(.el-table__row--level-1 .cell) {
  color: var(--el-text-color-regular, #606266);
}

/* 三级菜单：左侧橙色竖线 */
:deep(.el-table__row--level-2 td:first-child) {
  border-left: 3px solid #e6a23c;
  padding-left: 12px;
}
:deep(.el-table__row--level-2 .cell) {
  color: var(--el-text-color-secondary, #909399);
  font-size: 13px;
}
</style>
