<template>
  <div class="dict-page">
    <!-- 字典类型列表 -->
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>字典管理</span>
          <div>
            <el-button v-permission="'dict:type:delete'" type="danger" :disabled="!selectedIds.length" @click="handleBatchDelete">批量删除</el-button>
            <el-button type="success" @click="handleExport">导出</el-button>
            <el-button v-permission="'dict:type:add'" type="primary" @click="handleAddType">新增字典类型</el-button>
          </div>
        </div>
      </template>

      <el-form :model="typeFilters" inline class="mb-2">
        <el-form-item label="字典名称">
          <el-input v-model="typeFilters.dict_name" placeholder="字典名称" clearable style="width:160px" />
        </el-form-item>
        <el-form-item label="字典类型">
          <el-input v-model="typeFilters.dict_type" placeholder="类型编码" clearable style="width:160px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="typePage=1;fetchTypeList()">查询</el-button>
          <el-button @click="resetTypeFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="typeList" v-loading="typeLoading" stripe @selection-change="onTypeSelectionChange">
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="dict_name" label="字典名称" min-width="140" />
        <el-table-column prop="dict_type" label="字典类型编码" min-width="160" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val: number) => handleTypeStatusChange(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDataDrawer(row)">数据管理</el-button>
            <el-button v-permission="'dict:type:edit'" link type="primary" @click="handleEditType(row)">编辑</el-button>
            <el-popconfirm v-if="authStore.hasPermission('dict:type:delete')" title="确定删除？" @confirm="handleDeleteType(row)">
              <template #reference><el-button link type="danger">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="typeTotal > typePageSize" v-model:current-page="typePage" v-model:page-size="typePageSize"
        :page-sizes="[10, 20, 50]" :total="typeTotal" layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchTypeList" @size-change="typePage=1;fetchTypeList()" class="mt-3" />
    </el-card>

    <!-- 字典类型 新增/编辑 弹窗 -->
    <el-dialog v-model="typeFormVisible" :title="isTypeEdit ? '编辑字典类型' : '新增字典类型'" width="500px" @close="typeFormVisible = false">
      <el-form ref="typeFormRef" :model="typeForm" :rules="typeRules" label-width="100px">
        <el-form-item label="字典名称" prop="dict_name">
          <el-input v-model="typeForm.dict_name" placeholder="如 用户性别" />
        </el-form-item>
        <el-form-item label="字典类型编码" prop="dict_type">
          <el-input v-model="typeForm.dict_type" placeholder="如 sys_user_gender" :disabled="isTypeEdit" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="typeForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="typeForm.remark" type="textarea" :rows="3" placeholder="备注说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="typeFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="typeSubmitting" @click="handleSubmitType">确定</el-button>
      </template>
    </el-dialog>

    <!-- 字典数据管理抽屉 -->
    <el-drawer v-model="dataDrawerVisible" :title="`数据管理 — ${currentType?.dict_name || ''}`" size="700px">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
          <span>数据管理 — {{ currentType?.dict_name }}（{{ currentType?.dict_type }}）</span>
          <el-button type="primary" size="small" @click="handleAddData">新增数据项</el-button>
        </div>
      </template>

      <el-table :data="dataList" v-loading="dataLoading" stripe size="small">
        <template #empty><el-empty description="暂无数据项" /></template>
        <el-table-column prop="sort_order" label="排序" width="60" align="center" />
        <el-table-column prop="dict_label" label="字典标签" min-width="100" />
        <el-table-column prop="dict_value" label="字典键值" min-width="80" />
        <el-table-column label="样式" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.list_class" :type="row.list_class" size="small">{{ row.list_class }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="默认" width="60" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="warning" size="small">是</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEditData(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDeleteData(row)">
              <template #reference><el-button link type="danger" size="small">删除</el-button></template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="dataTotal > dataPageSize" v-model:current-page="dataPage" v-model:page-size="dataPageSize"
        :page-sizes="[10, 20, 50]" :total="dataTotal" layout="total, sizes, prev, pager, next"
        @current-change="fetchDataList" @size-change="dataPage=1;fetchDataList()" class="mt-3" />
    </el-drawer>

    <!-- 字典数据 新增/编辑 弹窗 -->
    <el-dialog v-model="dataFormVisible" :title="isDataEdit ? '编辑数据项' : '新增数据项'" width="500px" @close="dataFormVisible = false">
      <el-form ref="dataFormRef" :model="dataForm" :rules="dataRules" label-width="100px">
        <el-form-item label="字典标签" prop="dict_label">
          <el-input v-model="dataForm.dict_label" placeholder="如 男" />
        </el-form-item>
        <el-form-item label="字典键值" prop="dict_value">
          <el-input v-model="dataForm.dict_value" placeholder="如 1" />
        </el-form-item>
        <el-form-item label="样式类型">
          <el-select v-model="dataForm.list_class" placeholder="无" clearable style="width:100%">
            <el-option label="success 成功" value="success" />
            <el-option label="warning 警告" value="warning" />
            <el-option label="danger 危险" value="danger" />
            <el-option label="info 信息" value="info" />
            <el-option label="primary 主要" value="" />
          </el-select>
        </el-form-item>
        <el-form-item label="CSS 类名">
          <el-input v-model="dataForm.css_class" placeholder="可选" />
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="dataForm.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="是否默认">
          <el-switch v-model="dataForm.is_default" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="dataForm.status" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="dataForm.remark" type="textarea" :rows="2" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dataFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="dataSubmitting" @click="handleSubmitData">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance } from "element-plus";
import { useAuthStore } from "@/store/auth";
import {
  getDictTypeList, createDictType, updateDictType, deleteDictType,
  batchDeleteDictTypes, updateDictTypeStatus, exportDictTypes,
  getDictDataList, createDictData, updateDictData, deleteDictData,
  type DictType, type DictData,
} from "@/api/dict";

const authStore = useAuthStore();

// ─── 字典类型 ─────────────────────────────────────────────
const typeList = ref<DictType[]>([]);
const typeLoading = ref(false);
const typePage = ref(1);
const typePageSize = ref(10);
const typeTotal = ref(0);
const typeFilters = ref<{ dict_name: string; dict_type: string }>({ dict_name: "", dict_type: "" });
const selectedIds = ref<number[]>([]);

function resetTypeFilters() {
  typeFilters.value = { dict_name: "", dict_type: "" };
  typePage.value = 1;
  fetchTypeList();
}

async function fetchTypeList() {
  typeLoading.value = true;
  try {
    const res = await getDictTypeList({
      page: typePage.value, pageSize: typePageSize.value,
      dict_name: typeFilters.value.dict_name || undefined,
      dict_type: typeFilters.value.dict_type || undefined,
    });
    typeList.value = res.records;
    typeTotal.value = res.total;
  } finally { typeLoading.value = false; }
}

function onTypeSelectionChange(rows: DictType[]) { selectedIds.value = rows.map(r => r.id); }

async function handleTypeStatusChange(row: DictType, val: number) {
  await updateDictTypeStatus(row.id, val);
  ElMessage.success("状态已更新");
  fetchTypeList();
}

async function handleDeleteType(row: DictType) {
  try {
    await ElMessageBox.confirm(`确定删除字典「${row.dict_name}」？`, "提示");
    await deleteDictType(row.id);
    ElMessage.success("删除成功");
    fetchTypeList();
  } catch { /* cancel */ }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个字典类型？`, "提示");
    await batchDeleteDictTypes(selectedIds.value);
    ElMessage.success("批量删除成功");
    fetchTypeList();
  } catch { /* cancel */ }
}

async function handleExport() {
  try {
    const blob = await exportDictTypes() as unknown as Blob;
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `dict_types_${new Date().toISOString().slice(0, 10)}.csv`; a.click();
    URL.revokeObjectURL(url);
  } catch {
    ElMessage.error("导出失败");
  }
}

// 字典类型 新增/编辑
const typeFormVisible = ref(false);
const typeFormRef = ref<FormInstance>();
const typeSubmitting = ref(false);
const isTypeEdit = ref(false);
const editingTypeId = ref(0);
const typeForm = ref({ dict_name: "", dict_type: "", status: 1, remark: "" });
const typeRules = {
  dict_name: [{ required: true, message: "请输入字典名称", trigger: "blur" }],
  dict_type: [{ required: true, message: "请输入字典类型编码", trigger: "blur" }],
};

function handleAddType() {
  isTypeEdit.value = false;
  editingTypeId.value = 0;
  typeForm.value = { dict_name: "", dict_type: "", status: 1, remark: "" };
  typeFormVisible.value = true;
}

function handleEditType(row: DictType) {
  isTypeEdit.value = true;
  editingTypeId.value = row.id;
  typeForm.value = { dict_name: row.dict_name, dict_type: row.dict_type, status: row.status, remark: row.remark };
  typeFormVisible.value = true;
}

async function handleSubmitType() {
  try { await typeFormRef.value?.validate(); } catch { return; }
  typeSubmitting.value = true;
  try {
    if (isTypeEdit.value) {
      await updateDictType(editingTypeId.value, typeForm.value);
      ElMessage.success("更新成功");
    } else {
      await createDictType(typeForm.value);
      ElMessage.success("新增成功");
    }
    typeFormVisible.value = false;
    fetchTypeList();
  } finally { typeSubmitting.value = false; }
}

// ─── 字典数据 ─────────────────────────────────────────────
const dataDrawerVisible = ref(false);
const currentType = ref<DictType | null>(null);
const dataList = ref<DictData[]>([]);
const dataLoading = ref(false);
const dataPage = ref(1);
const dataPageSize = ref(20);
const dataTotal = ref(0);

function openDataDrawer(row: DictType) {
  currentType.value = row;
  dataPage.value = 1;
  fetchDataList();
  dataDrawerVisible.value = true;
}

async function fetchDataList() {
  if (!currentType.value) return;
  dataLoading.value = true;
  try {
    const res = await getDictDataList({
      page: dataPage.value, pageSize: dataPageSize.value,
      dict_type: currentType.value.dict_type,
    });
    dataList.value = res.records;
    dataTotal.value = res.total;
  } finally { dataLoading.value = false; }
}

async function handleDeleteData(row: DictData) {
  try {
    await ElMessageBox.confirm(`确定删除字典数据「${row.dict_label}」？`, "提示");
    await deleteDictData(row.id);
    ElMessage.success("删除成功");
    fetchDataList();
  } catch { /* cancel */ }
}

// 字典数据 新增/编辑
const dataFormVisible = ref(false);
const dataFormRef = ref<FormInstance>();
const dataSubmitting = ref(false);
const isDataEdit = ref(false);
const editingDataId = ref(0);
const dataForm = ref({
  dict_label: "", dict_value: "", css_class: "", list_class: "",
  sort_order: 0, status: 1, is_default: false, remark: "",
});
const dataRules = {
  dict_label: [{ required: true, message: "请输入字典标签", trigger: "blur" }],
  dict_value: [{ required: true, message: "请输入字典键值", trigger: "blur" }],
};

function handleAddData() {
  isDataEdit.value = false;
  editingDataId.value = 0;
  dataForm.value = { dict_label: "", dict_value: "", css_class: "", list_class: "", sort_order: 0, status: 1, is_default: false, remark: "" };
  dataFormVisible.value = true;
}

function handleEditData(row: DictData) {
  isDataEdit.value = true;
  editingDataId.value = row.id;
  dataForm.value = {
    dict_label: row.dict_label, dict_value: row.dict_value,
    css_class: row.css_class, list_class: row.list_class,
    sort_order: row.sort_order, status: row.status,
    is_default: row.is_default, remark: row.remark,
  };
  dataFormVisible.value = true;
}

async function handleSubmitData() {
  try { await dataFormRef.value?.validate(); } catch { return; }
  if (!currentType.value) return;
  dataSubmitting.value = true;
  try {
    const payload = { ...dataForm.value, dict_type: currentType.value.dict_type };
    if (isDataEdit.value) {
      await updateDictData(editingDataId.value, payload);
      ElMessage.success("更新成功");
    } else {
      await createDictData(payload);
      ElMessage.success("新增成功");
    }
    dataFormVisible.value = false;
    fetchDataList();
  } finally { dataSubmitting.value = false; }
}

onMounted(() => { fetchTypeList(); });
</script>

<style scoped>
.dict-page { padding: 0; }
.mb-2 { margin-bottom: 8px; }
.mt-3 { margin-top: 12px; }
</style>
