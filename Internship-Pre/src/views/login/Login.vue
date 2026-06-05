<template>
  <div class="login-container">
    <!-- 动态波浪背景 -->
    <div class="wave-bg">
      <svg class="wave-svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
        <path class="wave-1" fill="rgba(255,255,255,0.08)"
          d="M0,160L48,144C96,128,192,96,288,106.7C384,117,480,171,576,181.3C672,192,768,160,864,138.7C960,117,1056,107,1152,112C1248,117,1344,139,1392,149.3L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" />
        <path class="wave-2" fill="rgba(255,255,255,0.06)"
          d="M0,224L48,213.3C96,203,192,181,288,181.3C384,181,480,203,576,202.7C672,203,768,181,864,170.7C960,160,1056,160,1152,165.3C1248,171,1344,181,1392,186.7L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" />
        <path class="wave-3" fill="rgba(255,255,255,0.04)"
          d="M0,256L48,245.3C96,235,192,213,288,213.3C384,213,480,235,576,234.7C672,235,768,213,864,202.7C960,192,1056,192,1152,197.3C1248,203,1344,213,1392,218.7L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z" />
      </svg>
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
            <svg viewBox="0 0 40 40" width="40" height="40">
              <rect width="40" height="40" rx="10" fill="var(--el-color-primary)" />
              <text x="20" y="27" text-anchor="middle" fill="#fff" font-size="20" font-weight="bold">O</text>
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
              class="login-input"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              show-password
              :prefix-icon="Lock"
              class="login-input"
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

          <div class="login-actions">
            <el-button link type="primary" @click="showForgotDialog = true">
              忘记密码？
            </el-button>
          </div>
        </el-form>

        <div class="login-footer">
          <p class="copyright">&copy; 2026 组织架构管理系统. All rights reserved.</p>
        </div>
      </div>
    </div>

    <!-- 忘记密码对话框 -->
    <el-dialog v-model="showForgotDialog" title="找回密码" width="380px" align-center>
      <el-form :model="forgotForm" :rules="forgotRules" ref="forgotFormRef">
        <el-form-item prop="username">
          <el-input v-model="forgotForm.username" placeholder="请输入您的用户名" :prefix-icon="User" />
        </el-form-item>
      </el-form>
      <p class="forgot-tip">提交后管理员将在用户管理中看到重置请求，审批后密码重置为 123456</p>
      <template #footer>
        <el-button @click="showForgotDialog = false">取消</el-button>
        <el-button type="primary" :loading="forgotLoading" @click="handleForgotSubmit">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { useAuthStore } from "@/store/auth";
import { createResetRequest } from "@/api/user";

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

// 忘记密码
const showForgotDialog = ref(false);
const forgotLoading = ref(false);
const forgotFormRef = ref<FormInstance>();
const forgotForm = reactive({ username: "" });
const forgotRules: FormRules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
};

async function handleForgotSubmit() {
  const valid = await forgotFormRef.value?.validate().catch(() => false);
  if (!valid) return;
  forgotLoading.value = true;
  try {
    await createResetRequest(forgotForm.username);
    ElMessage.success("重置申请已提交，请联系管理员处理");
    showForgotDialog.value = false;
    forgotForm.username = "";
  } catch {
    // 错误由拦截器处理
  } finally {
    forgotLoading.value = false;
  }
}

onMounted(() => {
  if (authStore.token) {
    router.replace("/dashboard");
  }
});

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

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

/* ── 波浪背景 ──────────────────────────────────────────── */
.wave-bg {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 50%;
  pointer-events: none;
}

.wave-svg {
  width: 100%;
  height: 100%;
}

.wave-1 { animation: waveMove 8s ease-in-out infinite alternate; }
.wave-2 { animation: waveMove 10s ease-in-out infinite alternate-reverse; }
.wave-3 { animation: waveMove 12s ease-in-out infinite alternate; }

@keyframes waveMove {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50px); }
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
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
  transition: box-shadow 0.3s, background-color 0.3s;
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

.login-actions { text-align: center; margin-top: -8px; }
.login-actions .el-button { font-size: 13px; }
.forgot-tip { font-size: 12px; color: #909399; text-align: center; margin: -8px 0 0; }

 .dark .forgot-tip { color: #a0a2a8; }

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
  height: 44px;
  border-radius: 8px;
  font-size: 15px;
}

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
  background: linear-gradient(135deg, #1a1b23 0%, #1e1f2a 50%, #22232d 100%);
}

.dark .login-card {
  background: #1e1f28;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
}

.dark .login-title { color: #e0e2e8; }
.dark .login-subtitle { color: #a0a2a8; }
.dark .login-footer { border-top-color: #2a2b36; }
.dark .copyright { color: #585a60; }
.dark .el-input__wrapper { background: #2a2b36; box-shadow: 0 0 0 1px #333440; }
.dark .el-input__inner { color: #e0e2e8; }
.dark .el-checkbox__label { color: #a0a2a8; }
.dark .illustration-title,
.dark .illustration-desc,
.dark .feature-item { color: #c8cad0 !important; }

</style>