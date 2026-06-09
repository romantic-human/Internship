<template>
  <div class="page-container">
    <el-card shadow="never">
      <div class="card-header">
        <el-input
          v-model="searchName"
          placeholder="搜索知识库"
          clearable
          style="width: 240px"
          @clear="fetchData"
          @keyup.enter="fetchData"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button v-permission="'rag:kb:add'" type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon> 新建知识库
        </el-button>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="selection" width="45" />
        <el-table-column type="index" label="序号" width="60" align="center" :index="(i: number) => (currentPage - 1) * pageSize + i + 1" />
        <el-table-column prop="name" label="名称" min-width="140" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="doc_count" label="文档数" width="80" align="center" />
        <el-table-column prop="chunk_count" label="分块数" width="80" align="center" />
        <el-table-column prop="creator_name" label="创建者" width="100" />
        <el-table-column prop="create_time" label="创建时间" width="170" />
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-permission="'rag:kb:list'" type="primary" link size="small" @click="goDetail(row)">管理</el-button>
            <el-button v-permission="'rag:chat'" type="success" link size="small" @click="goChat(row)">问答</el-button>
            <el-button v-permission="'rag:kb:edit'" type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
            <el-button v-permission="'rag:kb:delete'" type="danger" link size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="currentPage=1;fetchData()"
        @current-change="fetchData"
      />
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑知识库' : '新建知识库'" width="480px" destroy-on-close>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用" />
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
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox, type FormInstance } from "element-plus";
import { Search, Plus } from "@element-plus/icons-vue";
import {
  getKnowledgeBaseList,
  createKnowledgeBase,
  updateKnowledgeBase,
  deleteKnowledgeBase,
  type KnowledgeBase,
} from "@/api/rag";

const router = useRouter();
const loading = ref(false);
const submitting = ref(false);
const tableData = ref<KnowledgeBase[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const searchName = ref("");

// 对话框
const dialogVisible = ref(false);
const isEdit = ref(false);
const editId = ref<number | null>(null);
const formRef = ref<FormInstance>();
const form = reactive({
  name: "",
  description: "",
  status: 1,
});
const rules = {
  name: [{ required: true, message: "请输入名称", trigger: "blur" }],
};

function openDialog(row?: KnowledgeBase) {
  if (row) {
    isEdit.value = true;
    editId.value = row.id;
    form.name = row.name;
    form.description = row.description;
    form.status = row.status;
  } else {
    isEdit.value = false;
    editId.value = null;
    form.name = "";
    form.description = "";
    form.status = 1;
  }
  dialogVisible.value = true;
}

async function fetchData() {
  loading.value = true;
  try {
    const res = await getKnowledgeBaseList({
      name: searchName.value,
      page: currentPage.value,
      page_size: pageSize.value,
    });
    tableData.value = res.records;
    total.value = res.total;
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false;
  }
}

async function handleSubmit() {
  if (!formRef.value) return;
  await formRef.value.validate();
  submitting.value = true;
  try {
    if (isEdit.value && editId.value) {
      await updateKnowledgeBase(editId.value, { ...form });
      ElMessage.success("更新成功");
    } else {
      await createKnowledgeBase({ ...form });
      ElMessage.success("创建成功");
    }
    dialogVisible.value = false;
    fetchData();
  } catch {
    // handled by interceptor
  } finally {
    submitting.value = false;
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("确定删除该知识库？", "提示");
    await deleteKnowledgeBase(id);
    ElMessage.success("删除成功");
    fetchData();
  } catch { /* cancel or error */ }
}

function goDetail(row: KnowledgeBase) {
  router.push({ path: "/rag/kb-detail", query: { id: row.id, name: row.name } });
}

function goChat(row: KnowledgeBase) {
  router.push({ path: "/rag/chat", query: { id: row.id, name: row.name } });
}

onMounted(fetchData);
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
