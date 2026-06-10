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

      <!-- 输入框 -->
      <div class="input-area">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="请输入你的问题..."
          :disabled="thinking || streaming"
          @keydown.enter.ctrl="handleSendStream"
        />
        <el-button
          type="primary"
          :loading="thinking || streaming"
          :disabled="!inputText.trim()"
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
import { ref, nextTick, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Delete, ChatDotRound, Loading } from "@element-plus/icons-vue";
import { chatWithKBStream, type ChatSource } from "@/api/rag";

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

function handleSendStream() {
  const question = inputText.value.trim();
  if (!question || thinking.value || streaming.value) return;

  messages.value.push({ role: "user", content: question });
  inputText.value = "";
  scrollToBottom();

  streaming.value = true;
  streamingContent.value = "";
  streamingSources.value = [];

  let fullContent = "";

  abortController.value = chatWithKBStream(
    kbId,
    question,
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
      scrollToBottom();
    },
    (err: string) => {
      ElMessage.error(err);
      streaming.value = false;
      streamingContent.value = "";
      streamingSources.value = [];
      abortController.value = null;
    },
  );
}

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
  align-items: flex-end;
  flex-shrink: 0;
}
</style>
