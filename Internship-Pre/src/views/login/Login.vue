<template>
  <div class="login-container">
    <!-- 深邃背景 -->
    <div class="bg-gradient" />
    <div class="bg-grid" />
    <div class="bg-glow">
      <div class="glow glow-1" />
      <div class="glow glow-2" />
      <div class="glow glow-3" />
    </div>

    <!-- 主内容 -->
    <div class="login-wrapper">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <!-- Logo -->
          <div class="brand-logo">
            <div class="logo-icon">
              <svg viewBox="0 0 48 48" width="48" height="48">
                <defs>
                  <linearGradient id="logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#818cf8" />
                    <stop offset="100%" stop-color="#c084fc" />
                  </linearGradient>
                </defs>
                <rect width="48" height="48" rx="12" fill="url(#logo-grad)" />
                <path d="M14 24L22 32L34 16" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none" />
              </svg>
            </div>
            <span class="logo-text">IntelliPlatform</span>
          </div>

          <!-- 标题 -->
          <h1 class="brand-title">
            <span class="title-line">企业智能</span>
            <span class="title-line accent">分析平台</span>
          </h1>

          <!-- 描述 -->
          <p class="brand-desc">
            集成知识库问答、自然语言查询、多模态理解<br />
            让 AI 驱动企业决策
          </p>

          <!-- 特性列表 -->
          <div class="features">
            <div class="feature" v-for="feat in features" :key="feat.label">
              <div class="feature-icon">
                <el-icon><component :is="feat.icon" /></el-icon>
              </div>
              <div>
                <div class="feature-label">{{ feat.label }}</div>
                <div class="feature-desc">{{ feat.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部装饰 -->
        <div class="brand-footer">
          <span>Powered by AI</span>
          <span class="dot" />
          <span>v2.0</span>
        </div>
      </div>

      <!-- 右侧登录区 -->
      <div class="login-section">
        <div class="login-card">
          <!-- 卡片头部 -->
          <div class="card-header">
            <h2>欢迎回来</h2>
            <p>登录您的账号以继续</p>
          </div>

          <!-- 登录表单 -->
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <div class="input-wrapper">
                <el-icon class="input-icon"><User /></el-icon>
                <el-input
                  v-model="form.username"
                  placeholder="用户名"
                  size="large"
                />
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <div class="input-wrapper">
                <el-icon class="input-icon"><Lock /></el-icon>
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="密码"
                  show-password
                  size="large"
                />
              </div>
            </el-form-item>

            <div class="form-options">
              <el-checkbox v-model="remember">记住密码</el-checkbox>
              <a class="forgot-link" href="#">忘记密码？</a>
            </div>

            <el-button
              type="primary"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              <span v-if="!loading">登 录</span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form>

          <!-- 底部 -->
          <div class="card-footer">
            <p>测试账号：admin / admin123</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, markRaw } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { User, Lock, ChatDotRound, Search, Picture } from "@element-plus/icons-vue";
import { useAuthStore } from "@/store/auth";

const router = useRouter();
const authStore = useAuthStore();
const formRef = ref<FormInstance>();
const loading = ref(false);
const remember = ref(localStorage.getItem("remember") === "true");

const form = reactive({
  username: localStorage.getItem("remember_username") || "",
  password: "",
});

const rules: FormRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const features = [
  { icon: markRaw(ChatDotRound), label: "智能问答", desc: "基于知识库的 AI 问答" },
  { icon: markRaw(Search), label: "自然语言查询", desc: "用自然语言查询数据库" },
  { icon: markRaw(Picture), label: "多模态理解", desc: "支持图片 + 文本混合输入" },
];

onMounted(() => {
  if (authStore.token) {
    router.replace("/dashboard");
  }
});

async function handleLogin() {
  try { await formRef.value?.validate(); } catch { return; }

  loading.value = true;
  try {
    await authStore.login(form.username, form.password);
    if (remember.value) {
      localStorage.setItem("remember", "true");
      localStorage.setItem("remember_username", form.username);
    } else {
      localStorage.setItem("remember", "false");
    }
    ElMessage.success("登录成功");
    await router.replace("/dashboard");
  } catch {
    // 错误已由 axios 拦截器处理
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
/* ── 容器 ──────────────────────────────────────── */
.login-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ── 背景层 ──────────────────────────────────────── */
.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a1033 30%, #0f172a 70%, #0a0a1a 100%);
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

.bg-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
}

.glow-1 {
  width: 600px;
  height: 600px;
  background: #6366f1;
  top: -200px;
  left: -100px;
  animation: float 20s ease-in-out infinite;
}

.glow-2 {
  width: 400px;
  height: 400px;
  background: #8b5cf6;
  bottom: -150px;
  right: -100px;
  animation: float 25s ease-in-out infinite reverse;
}

.glow-3 {
  width: 300px;
  height: 300px;
  background: #a78bfa;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 15s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(30px, -20px); }
  50% { transform: translate(-20px, 30px); }
  75% { transform: translate(20px, 20px); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.2; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.4; transform: translate(-50%, -50%) scale(1.1); }
}

/* ── 主布局 ──────────────────────────────────────── */
.login-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  width: 1000px;
  min-height: 600px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.5);
  animation: cardIn 0.8s ease-out;
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ── 左侧品牌区 ──────────────────────────────────────── */
.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(129, 140, 248, 0.15) 0%, transparent 70%);
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 48px;
}

.logo-icon {
  width: 48px;
  height: 48px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #c7d2fe;
  letter-spacing: 0.05em;
}

.brand-title {
  margin: 0 0 24px;
}

.title-line {
  display: block;
  font-size: 42px;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.title-line.accent {
  background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-desc {
  font-size: 15px;
  line-height: 1.7;
  color: #a5b4fc;
  margin-bottom: 40px;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.feature-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(165, 180, 252, 0.15);
  color: #a5b4fc;
  flex-shrink: 0;
}

.feature-label {
  font-size: 14px;
  font-weight: 600;
  color: #e0e7ff;
  margin-bottom: 2px;
}

.feature-desc {
  font-size: 13px;
  color: #818cf8;
}

.brand-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #6366f1;
  position: relative;
  z-index: 1;
}

.dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #6366f1;
}

/* ── 右侧登录区 ──────────────────────────────────────── */
.login-section {
  width: 420px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.login-card {
  width: 100%;
}

.card-header {
  margin-bottom: 36px;
}

.card-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}

.card-header p {
  font-size: 15px;
  color: #64748b;
  margin: 0;
}

/* ── 表单 ──────────────────────────────────────── */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 18px;
  z-index: 1;
}

.input-wrapper :deep(.el-input__wrapper) {
  padding-left: 44px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e2e8f0 !important;
  transition: all 0.2s ease !important;
}

.input-wrapper :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c7d2fe !important;
}

.input-wrapper :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.3) !important;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: -8px;
}

.forgot-link {
  font-size: 13px;
  color: #6366f1;
  text-decoration: none;
}

.forgot-link:hover {
  color: #4f46e5;
}

.login-btn {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  border: none !important;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(99, 102, 241, 0.45) !important;
}

.login-btn:active {
  transform: translateY(0);
}

.card-footer {
  margin-top: 32px;
  text-align: center;
}

.card-footer p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* ── 响应式 ──────────────────────────────────────── */
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    width: 90%;
    min-height: auto;
  }

  .brand-section {
    padding: 32px;
  }

  .brand-title .title-line {
    font-size: 28px;
  }

  .login-section {
    width: 100%;
    padding: 32px;
  }
}
</style>
