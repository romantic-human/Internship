<template>
  <div class="login-container">
    <div class="login-bg-shapes">
      <div class="shape shape-1" />
      <div class="shape shape-2" />
      <div class="shape shape-3" />
    </div>

    <div class="login-wrapper">
      <!-- 左侧装饰 -->
      <div class="login-illustration">
        <div class="illustration-content">
          <div class="illustration-icon">
            <svg viewBox="0 0 80 80" width="80" height="80">
              <rect x="8" y="20" width="64" height="48" rx="6" fill="currentColor" opacity="0.2" />
              <rect x="12" y="24" width="56" height="8" rx="2" fill="currentColor" opacity="0.4" />
              <circle cx="24" cy="42" r="4" fill="currentColor" opacity="0.3" />
              <rect x="32" y="40" width="24" height="4" rx="2" fill="currentColor" opacity="0.3" />
              <circle cx="24" cy="54" r="4" fill="currentColor" opacity="0.3" />
              <rect x="32" y="52" width="16" height="4" rx="2" fill="currentColor" opacity="0.3" />
            </svg>
          </div>
          <h3 class="illustration-title">企业级权限管理系统</h3>
          <p class="illustration-desc">基于 RBAC 模型，支持用户、角色、权限、菜单、部门统一管理</p>
          <div class="illustration-features">
            <div class="feature-item">
              <span class="feature-dot" />
              <span>统一身份认证</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>细粒度权限控制</span>
            </div>
            <div class="feature-item">
              <span class="feature-dot" />
              <span>操作审计日志</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录卡片 -->
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">
            <svg viewBox="0 0 48 48" width="48" height="48">
              <defs>
                <linearGradient id="lg" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#409eff" />
                  <stop offset="100%" stop-color="#6366f1" />
                </linearGradient>
              </defs>
              <rect width="48" height="48" rx="12" fill="url(#lg)" />
              <text x="24" y="31" text-anchor="middle" fill="#fff" font-size="22" font-weight="bold">O</text>
            </svg>
          </div>
          <h2 class="login-title">组织架构管理系统</h2>
          <p class="login-subtitle">欢迎回来，请登录您的账号</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          class="login-form"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              show-password
              :prefix-icon="Lock"
            />
          </el-form-item>

          <div class="login-options">
            <el-checkbox v-model="remember">记住密码</el-checkbox>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              {{ loading ? "登录中..." : "登 录" }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          <p class="copyright">&copy; 2026 组织架构管理系统. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
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

<style>
/* ── 容器 ──────────────────────────────────────────────── */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* ── 背景装饰形状 ──────────────────────────────────────── */
.login-bg-shapes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
  animation: shapeFloat 20s ease-in-out infinite;
}
.shape-1 {
  width: 600px; height: 600px;
  background: #6366f1;
  top: -200px; right: -100px;
  animation-delay: 0s;
}
.shape-2 {
  width: 400px; height: 400px;
  background: #409eff;
  bottom: -100px; left: -100px;
  animation-delay: -7s;
}
.shape-3 {
  width: 300px; height: 300px;
  background: #f472b6;
  top: 50%; left: 50%;
  animation-delay: -14s;
}
@keyframes shapeFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 20px) scale(0.95); }
}

/* ── 左右布局 ──────────────────────────────────────────── */
.login-wrapper {
  display: flex;
  align-items: center;
  gap: 48px;
  z-index: 1;
}

/* ── 左侧插图 ──────────────────────────────────────────── */
.login-illustration {
  display: none;
  color: #fff;
  max-width: 360px;
}

@media (min-width: 900px) {
  .login-illustration {
    display: block;
  }
}

.illustration-content {
  padding: 20px;
}

.illustration-icon {
  margin-bottom: 24px;
  opacity: 0.9;
}

.illustration-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 12px;
}

.illustration-desc {
  font-size: 14px;
  line-height: 1.6;
  opacity: 0.8;
  margin-bottom: 24px;
}

.illustration-features {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.85;
}

.feature-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #fff;
  opacity: 0.6;
}

/* ── 登录卡片 ──────────────────────────────────────────── */
.login-card {
  width: 400px;
  padding: 40px 36px 28px;
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15), 0 1px 2px rgba(0,0,0,0.05);
  transition: box-shadow 0.3s, background-color 0.3s, transform 0.3s;
  animation: cardIn 0.6s ease-out;
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(20px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.login-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px;
}

.login-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.login-form .el-input {
  --el-input-border-radius: 8px;
}

.login-input :deep(.el-input__wrapper) {
  transition: box-shadow 0.25s, border-color 0.25s;
}

.login-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--el-color-primary-light-7);
}

.login-options {
  display: flex;
  justify-content: flex-end;
  margin: -8px 0 16px;
}

.login-options :deep(.el-checkbox__label) {
  font-size: 13px;
  color: #909399;
}

.login-btn {
  width: 100%;
  height: 46px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
  transition: all 0.3s;
}
.login-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(64,158,255,0.4); }

/* ── 底部 ──────────────────────────────────────────────── */
.login-footer {
  text-align: center;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.copyright {
  font-size: 12px;
  color: #c0c4cc;
  margin: 0;
}

/* ── 夜间模式 ──────────────────────────────── */
.dark .login-container {
  background: linear-gradient(135deg, #0f1019 0%, #1a1b28 50%, #1e1f2a 100%);
}
.dark .login-card {
  background: rgba(30,31,40,0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
.dark .login-title { color: #e0e2e8; }
.dark .login-subtitle { color: #a0a2a8; }
.dark .login-footer { border-top-color: #2a2b36; }
.dark .copyright { color: #585a60; }
.dark .illustration-title,
.dark .illustration-desc,
.dark .feature-item { color: #c8cad0 !important; }
.dark .shape-1 { opacity: 0.08; }
.dark .shape-2 { opacity: 0.08; }
.dark .shape-3 { opacity: 0.06; }

</style>