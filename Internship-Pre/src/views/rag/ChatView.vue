<template>
  <div class="chat-container">
    <el-card shadow="never" class="chat-card">
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

        <!-- AI 思考中 -->
        <div v-if="thinking" class="message assistant">
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
          :disabled="thinking"
          @keydown.enter.ctrl="handleSend"
        />
        <el-button
          type="primary"
          :loading="thinking"
          :disabled="!inputText.trim()"
          @click="handleSend"
          style="margin-left: 8px; height: 54px"
        >
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Delete, ChatDotRound, Loading } from "@element-plus/icons-vue";
import { chatWithKB, type ChatSource } from "@/api/rag";

const route = useRoute();
const router = useRouter();
const kbId = Number(route.query.id);
const kbName = String(route.query.name || "知识库");

// 没有选择知识库时跳转到知识库列表
if (!kbId || isNaN(kbId)) {
  router.replace("/rag/kb-list");
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
  tokens_used?: number;
}

const messages = ref<Message[]>([]);
const inputText = ref("");
const thinking = ref(false);
const messageListRef = ref<HTMLElement>();

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  });
}

function renderMarkdown(text: string): string {
  // 简单的 Markdown 渲染：处理换行、加粗、列表
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

async function handleSend(e?: KeyboardEvent) {
  if (e) e.preventDefault();
  const question = inputText.value.trim();
  if (!question || thinking.value) return;

  messages.value.push({ role: "user", content: question });
  inputText.value = "";
  scrollToBottom();

  thinking.value = true;
  try {
    const res = await chatWithKB(kbId, question);
    messages.value.push({
      role: "assistant",
      content: res.answer,
      sources: res.sources,
      tokens_used: res.tokens_used,
    });
  } catch {
    messages.value.push({
      role: "assistant",
      content: "抱歉，处理您的问题时出现了错误，请稍后重试。",
    });
  } finally {
    thinking.value = false;
    scrollToBottom();
  }
}

function clearHistory() {
  messages.value = [];
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
