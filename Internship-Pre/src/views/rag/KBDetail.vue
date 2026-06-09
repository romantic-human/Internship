<template>
  <div class="page-container">
    <el-card shadow="never">
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
            <el-tag size="small">{{ row.file_type.toUpperCase() }}</el-tag>
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
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-permission="'rag:doc:upload'"
              v-if="row.status === 3"
              type="warning" link size="small"
              @click="handleReprocess(row.id)"
            >重新处理</el-button>
            <el-button type="primary" link size="small" @click="handlePreview(row)">预览</el-button>
            <el-button v-permission="'rag:doc:delete'" type="danger" link size="small" @click="handleDelete(row.id)">删除</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft, UploadFilled, View } from "@element-plus/icons-vue";
import {
  getDocumentList,
  uploadDocument,
  deleteDocument,
  reprocessDocument,
  getDocumentPreviewUrl,
  type Document,
} from "@/api/rag";

const route = useRoute();
const router = useRouter();
const kbId = Number(route.query.id);
const kbName = String(route.query.name || "知识库");

// 没有选择知识库时跳转到知识库列表
if (!kbId || isNaN(kbId)) {
  router.replace("/rag/kb-list");
}

const loading = ref(false);
const uploading = ref(false);
const tableData = ref<Document[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
let pollTimer: ReturnType<typeof setInterval> | null = null;

function formatSize(bytes: number): string {
  if (!bytes) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let i = 0;
  while (bytes >= 1024 && i < 3) { bytes /= 1024; i++; }
  return `${bytes.toFixed(1)} ${units[i]}`;
}

function startPolling() {
  stopPolling();
  pollTimer = setInterval(() => {
    const hasPending = tableData.value.some(d => d.status === 0 || d.status === 1);
    if (!hasPending) {
      stopPolling();
      return;
    }
    fetchData(true);
  }, 2000);
}

function stopPolling() {
  if (pollTimer !== null) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function handlePreview(row: Document) {
  const url = getDocumentPreviewUrl(row.id);
  if (row.file_type === "pdf") {
    window.open(url, "_blank");
  } else {
    ElMessageBox.alert(
      `<iframe src="${url}" style="width:100%;height:500px;border:none"></iframe>`,
      "文件预览",
      { dangerouslyUseHTMLString: true, showCancelButton: false, confirmButtonText: "关闭" },
    );
  }
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

async function fetchData(silent = false) {
  if (!kbId || isNaN(kbId)) return;
  if (!silent) loading.value = true;
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
    if (!silent) loading.value = false;
  }
}

async function handleBeforeUpload(file: File) {
  uploading.value = true;
  try {
    await uploadDocument(kbId, file);
    ElMessage.success("上传成功，正在处理...");
    fetchData();
    startPolling();
  } catch {
    // handled by interceptor
  } finally {
    uploading.value = false;
  }
  return false; // 阻止 el-upload 默认上传
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm("确定删除该文档？", "提示");
    await deleteDocument(id);
    ElMessage.success("删除成功");
    fetchData();
  } catch { /* cancel or error */ }
}

async function handleReprocess(id: number) {
  try {
    await reprocessDocument(id);
    ElMessage.success("正在重新处理");
    fetchData();
  } catch { /* handled by interceptor */ }
}

onMounted(() => {
  if (!kbId || isNaN(kbId)) return;
  fetchData();
  startPolling();
});
onUnmounted(stopPolling);
</script>

<style scoped>
.page-container { padding: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-left { display: flex; align-items: center; }
</style>
