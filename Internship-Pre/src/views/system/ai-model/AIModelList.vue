<template>
  <div class="ai-model-container">
    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="模型类型">
          <el-select v-model="searchForm.model_type" placeholder="全部" clearable style="width: 150px">
            <el-option label="对话模型" value="chat" />
            <el-option label="向量模型" value="embedding" />
            <el-option label="多模态模型" value="multimodal" />
          </el-select>
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="searchForm.provider" placeholder="全部" clearable style="width: 150px">
            <el-option label="智谱 AI" value="zhipu" />
            <el-option label="阿里云百炼" value="dashscope" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>模型配置列表</span>
          <el-button v-permission="'config:add'" type="primary" @click="handleAdd">新增模型</el-button>
        </div>
      </template>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column prop="provider_display" label="提供商" width="120" />
        <el-table-column prop="model_type_display" label="模型类型" width="120" />
        <el-table-column prop="model_name" label="模型名称" min-width="150" />
        <el-table-column prop="api_base_url" label="API 地址" min-width="200" show-overflow-tooltip />
        <el-table-column label="默认" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
            <el-button v-else link type="primary" size="small" @click="handleSetDefault(row)">设为默认</el-button>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'config:edit'" link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="primary" size="small" @click="handleTest(row)">测试</el-button>
            <el-button v-permission="'config:delete'" link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="如：智谱GLM-4-Flash" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-select v-model="form.provider" style="width: 100%">
            <el-option label="智谱 AI" value="zhipu" />
            <el-option label="阿里云百炼" value="dashscope" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型类型" prop="model_type">
          <el-select v-model="form.model_type" style="width: 100%">
            <el-option label="对话模型" value="chat" />
            <el-option label="向量模型" value="embedding" />
            <el-option label="多模态模型" value="multimodal" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="form.model_name" placeholder="如：glm-4-flash" />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="form.api_key" type="password" show-password placeholder="请输入 API Key" />
        </el-form-item>
        <el-form-item label="API 地址" prop="api_base_url">
          <el-input v-model="form.api_base_url" placeholder="如：https://open.bigmodel.cn/api/paas/v4" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import {
  getAIModelList,
  createAIModel,
  updateAIModel,
  deleteAIModel,
  setDefaultAIModel,
  testAIModelConnection,
  type AIModelConfig,
} from "@/api/ai-model";

// ── 搜索 ──
const searchForm = reactive({
  model_type: "",
  provider: "",
});

// ── 表格 ──
const loading = ref(false);
const tableData = ref<AIModelConfig[]>([]);
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

async function fetchData() {
  loading.value = true;
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };
    if (searchForm.model_type) params.model_type = searchForm.model_type;
    if (searchForm.provider) params.provider = searchForm.provider;
    const res = await getAIModelList(params);
    tableData.value = res.records;
    pagination.total = res.total;
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  pagination.page = 1;
  fetchData();
}

function handleReset() {
  searchForm.model_type = "";
  searchForm.provider = "";
  handleSearch();
}

function handleSizeChange() {
  pagination.page = 1;
  fetchData();
}

function handleCurrentChange() {
  fetchData();
}

// ── 弹窗 ──
const dialogVisible = ref(false);
const dialogTitle = ref("新增模型配置");
const formRef = ref<FormInstance>();
const submitting = ref(false);
const editingId = ref<number | null>(null);

const form = reactive({
  name: "",
  provider: "zhipu",
  model_type: "chat",
  model_name: "",
  api_key: "",
  api_base_url: "",
  is_default: false,
  status: 1,
  remark: "",
});

const rules: FormRules = {
  name: [{ required: true, message: "请输入配置名称", trigger: "blur" }],
  provider: [{ required: true, message: "请选择提供商", trigger: "change" }],
  model_type: [{ required: true, message: "请选择模型类型", trigger: "change" }],
  model_name: [{ required: true, message: "请输入模型名称", trigger: "blur" }],
  api_key: [{ required: true, message: "请输入 API Key", trigger: "blur" }],
  api_base_url: [{ required: true, message: "请输入 API 地址", trigger: "blur" }],
};

function resetForm() {
  editingId.value = null;
  form.name = "";
  form.provider = "zhipu";
  form.model_type = "chat";
  form.model_name = "";
  form.api_key = "";
  form.api_base_url = "";
  form.is_default = false;
  form.status = 1;
  form.remark = "";
}

function handleAdd() {
  resetForm();
  dialogTitle.value = "新增模型配置";
  dialogVisible.value = true;
}

function handleEdit(row: AIModelConfig) {
  editingId.value = row.id;
  dialogTitle.value = "编辑模型配置";
  form.name = row.name;
  form.provider = row.provider;
  form.model_type = row.model_type;
  form.model_name = row.model_name;
  form.api_key = row.api_key;
  form.api_base_url = row.api_base_url;
  form.is_default = row.is_default;
  form.status = row.status;
  form.remark = row.remark;
  dialogVisible.value = true;
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  submitting.value = true;
  try {
    if (editingId.value) {
      await updateAIModel(editingId.value, { ...form });
      ElMessage.success("更新成功");
    } else {
      await createAIModel({ ...form });
      ElMessage.success("新增成功");
    }
    dialogVisible.value = false;
    fetchData();
  } finally {
    submitting.value = false;
  }
}

// ── 操作 ──
async function handleSetDefault(row: AIModelConfig) {
  try {
    await setDefaultAIModel(row.id);
    ElMessage.success("设置成功");
    fetchData();
  } catch (e: any) {
    ElMessage.error(e.message || "设置失败");
  }
}

async function handleTest(row: AIModelConfig) {
  try {
    const res = await testAIModelConnection(row.id);
    ElMessage.success(`连接成功：${res.response}`);
  } catch (e: any) {
    ElMessage.error(e.message || "连接失败");
  }
}

async function handleDelete(row: AIModelConfig) {
  await ElMessageBox.confirm("确定删除该模型配置？", "提示", { type: "warning" });
  try {
    await deleteAIModel(row.id);
    ElMessage.success("删除成功");
    fetchData();
  } catch (e: any) {
    ElMessage.error(e.message || "删除失败");
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.ai-model-container {
  padding: 16px;
}

.search-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
