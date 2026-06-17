<template>
  <div class="notification-page">
    <el-card>
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span>消息通知 <el-badge v-if="unreadCount > 0" :value="unreadCount" class="ml-2" /></span>
          <div>
            <el-button v-permission="'notification:create'" type="primary" @click="openSendDialog">
              <el-icon><Plus /></el-icon> 发送通知
            </el-button>
            <el-button v-permission="'notification:read-all'" type="success" @click="handleMarkAllRead">全部已读</el-button>
            <el-button type="warning" @click="handleClearRead">清除已读</el-button>
          </div>
        </div>
      </template>

      <el-form :model="filters" inline class="mb-2">
        <el-form-item label="状态">
          <el-select v-model="filters.is_read" placeholder="全部" clearable style="width:100px">
            <el-option label="未读" value="false" />
            <el-option label="已读" value="true" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.type" placeholder="全部" clearable style="width:120px">
            <el-option label="系统通知" :value="0" />
            <el-option label="待办事项" :value="1" />
            <el-option label="提醒" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="page=1;fetchList()">查询</el-button>
          <el-button @click="filters.is_read='';filters.type=null;page=1;fetchList()">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="list" v-loading="loading" stripe>
        <template #empty><el-empty description="暂无通知" /></template>
        <el-table-column label="" width="30">
          <template #default="{ row }">
            <el-badge v-if="!row.is_read" is-dot type="danger" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <span :style="{ fontWeight: row.is_read ? 'normal' : 'bold' }">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="typeTagColor(row.notification_type)" size="small">{{ row.type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_read" type="info" size="small">已读</el-tag>
            <el-tag v-else type="danger" size="small">未读</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看</el-button>
            <el-button v-if="!row.is_read" link type="success" @click="handleMarkRead(row)">标记已读</el-button>
            <span v-permission="'notification:delete'">
              <el-popconfirm title="确定删除？" @confirm="handleDelete(row)">
                <template #reference><el-button link type="danger">删除</el-button></template>
              </el-popconfirm>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="fetchList"
        @size-change="page=1;fetchList()"
        class="mt-3"
      />
    </el-card>

    <!-- 发送通知弹窗 -->
    <el-dialog v-model="sendVisible" title="发送通知" width="520px" destroy-on-close>
      <el-form :model="sendForm" :rules="sendRules" ref="sendFormRef" label-width="100px">
        <el-form-item label="通知标题" prop="title">
          <el-input v-model="sendForm.title" placeholder="请输入通知标题" />
        </el-form-item>
        <el-form-item label="通知类型" prop="notification_type">
          <el-select v-model="sendForm.notification_type" style="width: 100%">
            <el-option label="系统通知" :value="0" />
            <el-option label="待办事项" :value="1" />
            <el-option label="提醒" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="通知内容" prop="content">
          <el-input v-model="sendForm.content" type="textarea" :rows="4" placeholder="请输入通知内容（可选）" />
        </el-form-item>
        <el-form-item label="发送范围">
          <el-radio-group v-model="sendScope">
            <el-radio value="all">全部活跃用户</el-radio>
            <el-radio value="select">指定用户</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="sendScope === 'select'" label="选择用户" prop="target_user_ids">
          <el-select v-model="sendForm.target_user_ids" multiple filterable remote
            :remote-method="searchUsers" :loading="userSearching" style="width: 100%"
            placeholder="搜索并选择用户">
            <el-option v-for="u in userOptions" :key="u.id" :label="u.username + ' (' + u.nickname + ')'" :value="u.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sendVisible = false">取消</el-button>
        <el-button type="primary" :loading="sending" @click="handleSend">发送</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="通知详情" width="500px">
      <template v-if="currentDetail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="标题">{{ currentDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ currentDetail.type_display }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ currentDetail.create_time }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-content">{{ currentDetail.content || "无详细内容" }}</div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import {
  getNotificationList,
  getNotificationDetail,
  deleteNotification,
  markNotificationRead,
  markAllNotificationsRead,
  clearReadNotifications,
  getUnreadCount,
  createNotification,
  type NotificationRecord,
} from "@/api/notification";
import { getUserList } from "@/api/user";
import type { FormInstance } from "element-plus";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";

const loading = ref(false);
const list = ref<NotificationRecord[]>([]);
const total = ref(0);
const page = ref(1);
const pageSize = ref(10);
const unreadCount = ref(0);

const filters = reactive({
  is_read: "" as string,
  type: null as number | null,
});

const detailVisible = ref(false);
const currentDetail = ref<NotificationRecord | null>(null);

function typeTagColor(t: number) {
  return t === 0 ? "" : t === 1 ? "warning" : "success";
}

async function fetchList() {
  loading.value = true;
  try {
    const params: Record<string, any> = { page: page.value, pageSize: pageSize.value };
    if (filters.is_read) params.is_read = filters.is_read;
    if (filters.type !== null) params.type = filters.type;
    const res = await getNotificationList(params);
    list.value = res.records;
    total.value = res.total;
    const uc = await getUnreadCount();
    unreadCount.value = uc.count;
  } finally {
    loading.value = false;
  }
}

async function handleViewDetail(row: NotificationRecord) {
  const detail = await getNotificationDetail(row.id);
  currentDetail.value = detail;
  detailVisible.value = true;
  row.is_read = true;
  const uc = await getUnreadCount();
  unreadCount.value = uc.count;
}

async function handleMarkRead(row: NotificationRecord) {
  await markNotificationRead(row.id);
  row.is_read = true;
  const uc = await getUnreadCount();
  unreadCount.value = uc.count;
  ElMessage.success("已标记为已读");
}

async function handleMarkAllRead() {
  await markAllNotificationsRead();
  list.value.forEach(r => r.is_read = true);
  unreadCount.value = 0;
  ElMessage.success("已全部标记为已读");
}

async function handleDelete(row: NotificationRecord) {
  try {
    await ElMessageBox.confirm("确定删除此通知？", "提示");
    await deleteNotification(row.id);
    ElMessage.success("删除成功");
    await fetchList();
  } catch { /* cancel */ }
}

async function handleClearRead() {
  try {
    const res = await clearReadNotifications();
    ElMessage.success(`已清除 ${res.count} 条已读通知`);
    await fetchList();
  } catch { /* handled */ }
}

// --- 发送通知 ---
const sendVisible = ref(false);
const sending = ref(false);
const sendScope = ref("all");
const sendFormRef = ref<FormInstance>();
const userOptions = ref<{ id: number; username: string; nickname: string }[]>([]);
const userSearching = ref(false);
const sendForm = reactive({
  title: "",
  notification_type: 0,
  content: "",
  target_user_ids: [] as number[],
});
const sendRules = {
  title: [{ required: true, message: "请输入通知标题", trigger: "blur" }],
};

function openSendDialog() {
  sendScope.value = "all";
  sendForm.title = "";
  sendForm.notification_type = 0;
  sendForm.content = "";
  sendForm.target_user_ids = [];
  sendVisible.value = true;
}

async function searchUsers(query: string) {
  if (!query) return;
  userSearching.value = true;
  try {
    const res = await getUserList({ username: query, page: 1, pageSize: 20 });
    userOptions.value = res.records.map(r => ({ id: r.id, username: r.username, nickname: r.nickname || r.username }));
  } finally {
    userSearching.value = false;
  }
}

async function handleSend() {
  if (!sendFormRef.value) return;
  try { await sendFormRef.value.validate(); } catch { return; }
  sending.value = true;
  try {
    const payload: any = {
      title: sendForm.title,
      notification_type: sendForm.notification_type,
    };
    if (sendForm.content) payload.content = sendForm.content;
    if (sendScope.value === "select") {
      payload.target_user_ids = sendForm.target_user_ids;
    }
    const res = await createNotification(payload);
    ElMessage.success(`已发送给 ${res.count} 人`);
    sendVisible.value = false;
    await fetchList();
  } finally {
    sending.value = false;
  }
}

onMounted(fetchList);
</script>

<style scoped>
.mb-2 { margin-bottom: 12px; }
.mt-3 { margin-top: 16px; }
.ml-2 { margin-left: 8px; }
.detail-content { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 4px; line-height: 1.8; white-space: pre-wrap; }
</style>
