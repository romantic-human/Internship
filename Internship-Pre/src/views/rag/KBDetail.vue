<template>
  <div class="page-container">
    <!-- 未选择知识库时的引导提示 -->
    <div v-if="!validKb" class="empty-state" style="padding:80px 0;text-align:center">
      <el-icon :size="64" color="#c0c4cc"><FolderOpened /></el-icon>
      <p style="font-size:16px;color:#606266;margin:16px 0 8px">文档管理</p>
      <p style="color:#909399;margin-bottom:20px">请先前往知识库列表，选择一个知识库后点击"管理"按钮进入文档管理</p>
      <el-button type="primary" @click="router.push('/rag/kb-list')">前往知识库列表</el-button>
    </div>

    <!-- 已选择知识库时的正常内容 -->
    <el-card v-else shadow="never">
      <div class="card-header">
        <div class="header-left">
          <el-button @click="$router.push('/rag/kb-list')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <h3 style="margin: 0 0 0 12px">{{ kbName }}</h3>
        </div>
        <el-upload
          v-permission="'rag:doc:upload'"
          :before-upload="handleBeforeUpload"
          :show-file-list="false"
          accept=".pdf,.txt,.md,.docx"
        >
          <el-button type="primary" :loading="uploading">
            <el-icon><UploadFilled /></el-icon> 上传文档
          </el-button>
        </el-upload>
      </div>

      <el-table :data="tableData" v-loading="loading" stripe border>
        <template #empty><el-empty description="暂无数据" /></template>
        <el-table-column type="index" label="序号" width="60" align="center" :index="(i: number) => (currentPage - 1) * pageSize + i + 1" />
        <el-table-column prop="file_name" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="file_type" label="类型" width="70" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ (row.file_type || '').toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="100" align="center">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="80" align="center" />
        <el-table-column prop="status_display" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error_message" label="错误信息" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.status === 3" style="color: #f56c6c">{{ row.error_message }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="上传时间" width="170" />
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 3"
              type="warning" link size="small"
              @click="handleReprocess(row)"
            >
              <el-icon><RefreshRight /></el-icon> 重新处理
            </el-button>
            <el-popconfirm title="确认删除此文档？" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link size="small" v-permission="'rag:doc:delete'">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
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
        @size-change="currentPage = 1; fetchData()"
        @current-change="fetchData"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, UploadFilled, Delete, RefreshRight, FolderOpened } from "@element-plus/icons-vue";
import {
  getDocumentList,
  uploadDocument,
  deleteDocument,
  reprocessDocument,
  type Document,
} from "@/api/rag";

const route = useRoute();
const router = useRouter();
const kbId = Number(route.query.id);
const kbName = String(route.query.name || "知识库");
const validKb = !isNaN(kbId) && kbId > 0;

// 没有选择知识库时显示引导提示（不跳转）

const loading = ref(false);
const uploading = ref(false);
const tableData = ref<Document[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

function formatSize(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  while (bytes >= 1024 && i < 3) { bytes /= 1024; i++; }
  return `${bytes.toFixed(1)} ${units[i]}`;
}

function statusType(status: number): string {
  switch (status) {
    case 0: return "info";
    case 1: return "warning";
    case 2: return "success";
    case 3: return "danger";
    default: return "info";
  }
}

async function fetchData() {
  if (!validKb) return;
  loading.value = true;
  try {
    const res = await getDocumentList({
      knowledge_base: kbId,
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

async function handleBeforeUpload(file: File) {
  uploading.value = true;
  try {
    await uploadDocument(kbId, file);
    ElMessage.success("上传成功，正在处理...");
    fetchData();
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false;
  }
  return false; // 阻止 el-upload 默认上传
}

async function handleDelete(id: number) {
  try {
    await deleteDocument(id);
    ElMessage.success("删除成功");
    fetchData();
  } catch {
    // handled by interceptor
  }
}

async function handleReprocess(row: Document) {
  try {
    await reprocessDocument(row.id);
    ElMessage.success("正在重新处理");
    fetchData();
  } catch {
    // handled by interceptor
  }
}

onMounted(fetchData);
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-left { display: flex; align-items: center; }
</style>
