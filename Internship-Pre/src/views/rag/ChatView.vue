<template>
  <div class="chat-container">
    <div v-if="!validKb" class="empty-state" style="padding:80px 0;text-align:center">
      <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
      <p style="font-size:16px;color:#606266;margin:16px 0 8px">AI 智能问答</p>
      <p style="color:#909399;margin-bottom:20px">请先前往知识库列表，选择一个知识库后点击"问答"按钮</p>
      <el-button type="primary" @click="router.push('/rag/kb-list')">前往知识库列表</el-button>
    </div>

    <el-card v-else shadow="never" class="chat-card">
      <div class="card-header">
        <div class="header-left">
          <el-button @click="$router.push('/rag/kb-list')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <h3 style="margin: 0 0 0 12px">AI 问答 - {{ kbName }}</h3>
        </div>
        <el-button text @click="clearHistory">
          <el-icon><Delete /></el-icon> 清空对话
        </el-button>
      </div>

      <div class="message-list" ref="messageListRef">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
          <p>输入问题，基于知识库文档进行智能问答</p>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="message-avatar">
            <el-avatar :size="36" :style="msg.role === 'user' ? { background: '#409eff' } : { background: '#67c23a' }">
              {{ msg.role === 'user' ? '我' : 'AI' }}
            </el-avatar>
          </div>
          <div class="message-body">
            <div class="message-content" v-html="renderMarkdown(msg.content)"></div>
            <div v-if="msg.sources && msg.sources.length > 0" class="message-sources">
              <el-collapse>
                <el-collapse-item title="参考来源">
                  <div v-for="(src, si) in msg.sources" :key="si" class="source-item">
                    <div class="source-header">
                      <el-tag size="small">{{ src.document_name }}</el-tag>
                      <span class="source-meta">块 #{{ src.chunk_index }}</span>
                      <span class="source-meta">相关度: {{ (src.relevance_score * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="source-content">{{ src.content }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
            <div v-if="msg.tokens_used" class="message-meta">
              消耗 {{ msg.tokens_used }} tokens
            </div>
          </div>
        </div>

        <div v-if="streaming" class="message assistant">
          <div class="message-avatar">
            <el-avatar :size="36" style="background: #67c23a">AI</el-avatar>
          </div>
          <div class="message-body">
            <div class="message-content" v-html="renderMarkdown(streamingContent)"></div>
            <div v-if="streamingSources && streamingSources.length > 0" class="message-sources">
              <el-collapse>
                <el-collapse-item title="参考来源">
                  <div v-for="(src, si) in streamingSources" :key="si" class="source-item">
                    <div class="source-header">
                      <el-tag size="small">{{ src.document_name }}</el-tag>
                      <span class="source-meta">块 #{{ src.chunk_index }}</span>
                      <span class="source-meta">相关度: {{ (src.relevance_score * 100).toFixed(1) }}%</span>
                    </div>
                    <div class="source-content">{{ src.content }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>

        <div v-if="thinking && !streaming" class="message assistant">
          <div class="message-avatar">
            <el-avatar :size="36" style="background: #67c23a">AI</el-avatar>
          </div>
          <div class="message-body">
            <div class="message-content">
              <el-icon class="is-loading"><Loading /></el-icon> 正在思考...
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-toolbar">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            multiple
            accept="image/jpeg,image/png,image/gif,image/webp"
            :show-file-list="false"
            :on-change="handleImageSelect"
          >
            <el-button :disabled="thinking || streaming" text>
              <el-icon><PictureFilled /></el-icon> 图片
            </el-button>
          </el-upload>
        </div>
        <div v-if="selectedImages.length > 0" class="image-preview-area">
          <div v-for="(img, idx) in selectedImages" :key="idx" class="image-preview-item">
            <el-image :src="img.url" fit="cover" style="width: 64px; height: 64px; border-radius: 6px" />
            <el-button class="image-remove-btn" size="small" circle text @click="removeImage(idx)">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="input-row">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="2"
            placeholder="请输入你的问题... (Ctrl+Enter 发送)"
            :disabled="thinking || streaming"
            @keydown.enter.ctrl="handleSendMultimodal"
          />
          <el-button
            type="primary"
            :loading="thinking || streaming"
            :disabled="!inputText.trim()"
            @click="handleSendMultimodal"
            style="margin-left: 8px; height: 54px"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Delete, ChatDotRound, Loading, PictureFilled, Close } from "@element-plus/icons-vue";
import { chatWithKBStream, chatMultimodalStream, type ChatSource } from "@/api/rag";

const route = useRoute();
const router = useRouter();
const kbId = Number(route.query.id);
const kbName = String(route.query.name || "知识库");

if (!kbId || isNaN(kbId)) {
}
const validKb = !!kbId && !isNaN(kbId);

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  tokens_used?: number;
}

const STORAGE_KEY = `chat_history_${kbId}`;

function loadHistory(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(msgs: Message[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(msgs));
}

const messages = ref<Message[]>(loadHistory());
const inputText = ref("");
const thinking = ref(false);
const streaming = ref(false);
const streamingContent = ref("");
const streamingSources = ref<ChatSource[]>([]);
const abortController = ref<AbortController | null>(null);
const messageListRef = ref<HTMLElement>();
const selectedImages = ref<{ file: File; url: string }[]>([]);
const uploadRef = ref();

watch(messages, (msgs) => saveHistory(msgs), { deep: true });

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
}

function renderMarkdown(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

function handleImageSelect(uploadFile: any) {
  const file = uploadFile.raw as File;
  if (!file) return;
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning("图片不能超过 10MB");
    return;
  }
  selectedImages.value.push({ file, url: URL.createObjectURL(file) });
}

function removeImage(idx: number) {
  const img = selectedImages.value[idx];
  if (img) URL.revokeObjectURL(img.url);
  selectedImages.value.splice(idx, 1);
}

function handleSendMultimodal() {
  const question = inputText.value.trim();
  if (!question || thinking.value || streaming.value) return;

  if (selectedImages.value.length > 0) {
    handleSendStream(true);
  } else {
    handleSendStream(false);
  }
}

function handleSendStream(multimodal = false) {
  const question = inputText.value.trim();
  if (!question || thinking.value || streaming.value) return;

  const userMsg: Message = { role: "user", content: question };
  messages.value.push(userMsg);
  inputText.value = "";

  const images = [...selectedImages.value];
  selectedImages.value = [];
  scrollToBottom();

  streaming.value = true;
  streamingContent.value = "";
  streamingSources.value = [];

  let fullContent = "";

  const onToken = (token: string) => {
    fullContent += token;
    streamingContent.value = fullContent;
    scrollToBottom();
  };

  const onSources = (sources: ChatSource[]) => {
    streamingSources.value = sources;
  };

  const onDone = () => {
    if (fullContent) {
      messages.value.push({
        role: "assistant",
        content: fullContent,
        sources: streamingSources.value,
      });
    }
    streaming.value = false;
    streamingContent.value = "";
    streamingSources.value = [];
    abortController.value = null;
    scrollToBottom();
  };

  const onError = (err: string) => {
    ElMessage.error(err);
    streaming.value = false;
    streamingContent.value = "";
    streamingSources.value = [];
    abortController.value = null;
  };

  if (multimodal) {
    abortController.value = chatMultimodalStream(
      kbId, question, images.map((i) => i.file),
      onToken, onSources, onDone, onError,
    );
  } else {
    abortController.value = chatWithKBStream(
      kbId, question, onToken, onSources, onDone, onError,
    );
  }
}

onUnmounted(() => {
  abortController.value?.abort();
});

function clearHistory() {
  messages.value = [];
  localStorage.removeItem(STORAGE_KEY);
}
</script>

<style scoped>
.chat-container { height: calc(100vh - 140px); display: flex; flex-direction: column; }
.chat-card { flex: 1; display: flex; flex-direction: column; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0; }
.header-left { display: flex; align-items: center; }

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  min-height: 200px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.message {
  display: flex;
  padding: 8px 16px;
  margin-bottom: 4px;
}

.message.user { flex-direction: row-reverse; }
.message.user .message-avatar { margin-left: 12px; }
.message.user .message-body { align-items: flex-end; }

.message.assistant .message-avatar { margin-right: 12px; }

.message-body {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
}

.message.user .message-content {
  background: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.message.assistant .message-content {
  background: #f4f4f5;
  color: #303133;
  border-top-left-radius: 4px;
}

.message-sources { margin-top: 8px; }
.message-sources :deep(.el-collapse) { border: none; }
.message-sources :deep(.el-collapse-item__header) { font-size: 12px; color: #909399; height: 28px; }
.source-item { margin-bottom: 8px; padding: 8px; background: #fafafa; border-radius: 6px; }
.source-header { display: flex; gap: 8px; align-items: center; margin-bottom: 4px; }
.source-meta { font-size: 12px; color: #909399; }
.source-content { font-size: 12px; color: #606266; line-height: 1.5; }

.message-meta { font-size: 11px; color: #c0c4cc; margin-top: 4px; }

.input-area {
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  gap: 6px;
}

.input-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
}

.image-preview-area {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 4px 0;
}

.image-preview-item {
  position: relative;
  flex-shrink: 0;
}

.image-remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  padding: 0;
}

.input-row {
  display: flex;
  align-items: flex-end;
}
</style>
