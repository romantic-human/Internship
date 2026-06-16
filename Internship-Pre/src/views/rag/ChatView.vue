<template>
  <div class="chat-container">
    <!-- 未选择知识库时的引导提示 -->
    <div v-if="!validKb" class="empty-state" style="padding:80px 0;text-align:center">
      <el-icon :size="64" color="#c0c4cc"><ChatDotRound /></el-icon>
      <p style="font-size:16px;color:#606266;margin:16px 0 8px">AI 智能问答</p>
      <p style="color:#909399;margin-bottom:20px">请先前往知识库列表，选择一个知识库后点击"问答"按钮</p>
      <el-button type="primary" @click="router.push('/rag/kb-list')">前往知识库列表</el-button>
    </div>

    <!-- 已选择知识库时的对话区域 -->
    <el-card v-else shadow="never" class="chat-card">
      <div class="card-header">
        <div class="header-left">
          <el-button @click="$router.push('/rag/kb-list')">
            <el-icon><ArrowLeft /></el-icon> 返回
          </el-button>
          <h3 style="margin: 0 0 0 12px">AI 问答 - {{ kbName }}</h3>
          <el-tag v-if="imagePreview" type="success" size="small" style="margin-left: 12px">多模态模式</el-tag>
        </div>
        <el-button text @click="clearHistory">
          <el-icon><Delete /></el-icon> 清空对话
        </el-button>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
          <p>输入问题，基于知识库文档进行智能问答</p>
          <p style="font-size:12px;color:#c0c4cc">支持上传图片进行多模态问答</p>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <el-avatar :size="36" :style="msg.role === 'user' ? { background: '#409eff' } : { background: '#67c23a' }">
              {{ msg.role === 'user' ? '我' : 'AI' }}
            </el-avatar>
          </div>
          <div class="message-body">
            <!-- 用户消息中的图片 -->
            <div v-if="msg.image" class="message-image">
              <el-image
                :src="msg.image"
                :preview-src-list="[msg.image]"
                fit="contain"
                style="max-width: 200px; max-height: 200px; border-radius: 8px;"
              />
            </div>
            <div class="message-content" v-html="renderMarkdown(msg.content)"></div>

            <!-- 来源引用 -->
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

        <!-- AI 思考中（流式输出中） -->
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

        <!-- AI 思考中（非流式） -->
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

      <!-- 图片预览区 -->
      <div v-if="imagePreview" class="image-preview-area">
        <div class="preview-wrapper">
          <el-image
            :src="imagePreview"
            fit="contain"
            style="width: 60px; height: 60px; border-radius: 6px; border: 1px solid #dcdfe6;"
          />
          <el-button
            type="danger"
            :icon="Delete"
            circle
            size="small"
            style="margin-left: 8px;"
            @click="clearImage"
          />
          <span style="font-size: 12px; color: #909399; margin-left: 8px;">已选择图片</span>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <!-- 图片上传按钮 -->
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="false"
          accept="image/*"
          :on-change="handleImageSelect"
          style="margin-right: 8px;"
        >
          <el-button
            :disabled="thinking || streaming"
            style="height: 54px;"
          >
            <el-icon size="20"><Picture /></el-icon>
          </el-button>
        </el-upload>

        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          :placeholder="imagePreview ? '请描述你关于图片的问题...' : '请输入你的问题...'"
          :disabled="thinking || streaming"
          @keydown.enter.ctrl="handleSendStream"
        />
        <el-button
          type="primary"
          :loading="thinking || streaming"
          :disabled="(!inputText.trim() && !imagePreview)"
          @click="handleSendStream"
          style="margin-left: 8px; height: 54px"
        >
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Delete, ChatDotRound, Loading, Picture } from "@element-plus/icons-vue";
import { chatWithKBStream, type ChatSource } from "@/api/rag";
import type { UploadFile } from "element-plus";

const route = useRoute();
const router = useRouter();
const kbId = Number(route.query.id);
const kbName = String(route.query.name || "知识库");

if (!kbId || isNaN(kbId)) {
  // 不跳转，显示引导提示
}
const validKb = !!kbId && !isNaN(kbId);

interface Message {
  role: "user" | "assistant";
  content: string;
  image?: string;  // 用户消息附带的图片（data:image/...;base64,...）
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
  // 不保存图片到 localStorage（太大），只保存文本
  const lite = msgs.map(({ image, ...rest }) => rest);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(lite));
}

const messages = ref<Message[]>(loadHistory());
const inputText = ref("");
const thinking = ref(false);
const streaming = ref(false);
const streamingContent = ref("");
const streamingSources = ref<ChatSource[]>([]);
const abortController = ref<AbortController | null>(null);
const messageListRef = ref<HTMLElement>();

// 图片相关
const imagePreview = ref<string>("");  // 预览用的 data URL
const imageBase64 = ref<string>("");   // 发送给后端的纯 base64

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

/** 选择图片后处理 */
function handleImageSelect(file: UploadFile) {
  const rawFile = file.raw;
  if (!rawFile) return;

  // 校验类型
  if (!rawFile.type.startsWith("image/")) {
    ElMessage.warning("请选择图片文件");
    return;
  }

  // 校验大小（10MB）
  if (rawFile.size > 10 * 1024 * 1024) {
    ElMessage.warning("图片大小不能超过 10MB");
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    const dataUrl = e.target?.result as string;
    imagePreview.value = dataUrl;
    // 提取纯 base64（去掉 data:image/...;base64, 前缀）
    imageBase64.value = dataUrl.split(",")[1] || "";
  };
  reader.readAsDataURL(rawFile);
}

function clearImage() {
  imagePreview.value = "";
  imageBase64.value = "";
}

function handleSendStream() {
  const question = inputText.value.trim();
  if ((!question && !imageBase64.value) || thinking.value || streaming.value) return;

  // 如果有图片但没有问题，给一个默认问题
  const finalQuestion = question || "请描述这张图片的内容";

  messages.value.push({
    role: "user",
    content: question || "（图片问答）",
    image: imagePreview.value || undefined,
  });
  inputText.value = "";
  scrollToBottom();

  streaming.value = true;
  streamingContent.value = "";
  streamingSources.value = [];

  let fullContent = "";

  abortController.value = chatWithKBStream(
    kbId,
    finalQuestion,
    (token: string) => {
      fullContent += token;
      streamingContent.value = fullContent;
      scrollToBottom();
    },
    (sources: ChatSource[]) => {
      streamingSources.value = sources;
    },
    () => {
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
      clearImage();  // 发送完成后清除图片
      scrollToBottom();
    },
    (err: string) => {
      ElMessage.error(err);
      streaming.value = false;
      streamingContent.value = "";
      streamingSources.value = [];
      abortController.value = null;
    },
    imageBase64.value || undefined,  // 传递图片
  );
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

.message-image {
  margin-bottom: 8px;
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

.image-preview-area {
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 8px;
  flex-shrink: 0;
}

.preview-wrapper {
  display: flex;
  align-items: center;
}

.input-area {
  display: flex;
  align-items: flex-end;
  flex-shrink: 0;
}
</style>
