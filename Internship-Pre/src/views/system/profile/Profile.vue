<template>
  <div class="profile-container">
    <h2 class="page-title">个人中心</h2>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- ═══════════════ Tab 1: 基本资料 ═══════════════ -->
      <el-tab-pane label="基本资料" name="info">
        <el-form
          ref="infoFormRef"
          :model="profileForm"
          :rules="infoRules"
          label-width="100px"
          size="large"
          class="profile-form"
        >
          <el-form-item label="用户名">
            <el-input :model-value="authStore.userInfo?.username" disabled />
          </el-form-item>

          <el-form-item label="昵称" prop="nickname">
            <el-input v-model="profileForm.nickname" placeholder="请输入昵称" />
          </el-form-item>

          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="手机号" prop="telephone">
            <el-input v-model="profileForm.telephone" placeholder="请输入手机号" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="infoSaving" @click="saveProfile">
              保存修改
            </el-button>
            <el-button @click="resetProfileForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- ═══════════════ Tab 2: 修改密码 ═══════════════ -->
      <el-tab-pane label="修改密码" name="password">
        <el-form
          ref="pwdFormRef"
          :model="passwordForm"
          :rules="pwdRules"
          label-width="120px"
          size="large"
          class="profile-form"
        >
          <el-form-item label="旧密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              show-password
              placeholder="请输入旧密码"
            />
          </el-form-item>

          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              show-password
              placeholder="请输入新密码（至少6位）"
            />
          </el-form-item>

          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              show-password
              placeholder="请再次输入新密码"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="pwdSaving" @click="handleChangePassword">
              修改密码
            </el-button>
            <el-button @click="resetPasswordForm">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- ═══════════════ Tab 3: 头像上传 ═══════════════ -->
      <el-tab-pane label="头像设置" name="avatar">
        <div class="avatar-tab">
          <div class="avatar-preview">
            <el-avatar
              :size="120"
              :src="avatarUrl || undefined"
              shape="square"
            >
              {{ authStore.userInfo?.nickname?.charAt(0) || "U" }}
            </el-avatar>
            <p class="avatar-hint">当前头像</p>
          </div>

          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :show-file-list="false"
            accept=".jpg,.jpeg,.png,.gif,.webp"
            :on-change="handleFileChange"
          >
            <template #trigger>
              <el-button type="primary">选择图片</el-button>
            </template>
          </el-upload>

          <div v-if="selectedFile" class="avatar-new-preview">
            <p>新头像预览：</p>
            <el-avatar :size="120" :src="previewUrl" shape="square" />
            <div class="avatar-actions">
              <el-button type="success" :loading="avatarUploading" @click="handleUploadAvatar">
                确认上传
              </el-button>
              <el-button @click="cancelAvatar">取消</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import type { UploadInstance, UploadRawFile } from "element-plus";
import { useAuthStore } from "@/store/auth";
import {
  getUserProfile,
  updateUserProfile,
  updatePassword,
  uploadAvatar,
} from "@/api/user";

const authStore = useAuthStore();

const activeTab = ref("info");

// ── 基本资料 ─────────────────────────────────────────────
const infoFormRef = ref<FormInstance>();
const infoSaving = ref(false);

const profileForm = reactive({
  nickname: "",
  real_name: "",
  email: "",
  telephone: "",
});

const infoRules: FormRules = {
  nickname: [{ max: 64, message: "昵称不能超过64个字符", trigger: "blur" }],
  email: [{ type: "email", message: "请输入正确的邮箱格式", trigger: "blur" }],
  telephone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: "请输入正确的手机号格式",
      trigger: "blur",
    },
  ],
};

async function loadProfile() {
  try {
    const data: any = await getUserProfile();
    profileForm.nickname = data.nickname || "";
    profileForm.real_name = data.real_name || "";
    profileForm.email = data.email || "";
    profileForm.telephone = data.telephone || "";
  } catch {
    // 错误已由拦截器处理
  }
}

function resetProfileForm() {
  loadProfile();
}

async function saveProfile() {
  const valid = await infoFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  infoSaving.value = true;
  try {
    const res = await updateUserProfile({
      nickname: profileForm.nickname,
      real_name: profileForm.real_name,
      email: profileForm.email,
      telephone: profileForm.telephone,
    });
    ElMessage.success("保存成功");
    // 更新 store 中的昵称
    if (authStore.userInfo) {
      authStore.userInfo.nickname = profileForm.nickname;
    }
  } catch {
    // 错误已由拦截器处理
  } finally {
    infoSaving.value = false;
  }
}

// ── 修改密码 ─────────────────────────────────────────────
const pwdFormRef = ref<FormInstance>();
const pwdSaving = ref(false);

const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const validateConfirm = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const pwdRules: FormRules = {
  oldPassword: [{ required: true, message: "请输入旧密码", trigger: "blur" }],
  newPassword: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "新密码至少6位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请再次输入新密码", trigger: "blur" },
    { validator: validateConfirm, trigger: "blur" },
  ],
};

function resetPasswordForm() {
  passwordForm.oldPassword = "";
  passwordForm.newPassword = "";
  passwordForm.confirmPassword = "";
}

async function handleChangePassword() {
  const valid = await pwdFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  pwdSaving.value = true;
  try {
    await updatePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword,
    });
    ElMessage.success("密码修改成功，请重新登录");
    resetPasswordForm();
    authStore.logout();
  } catch {
    // 错误已由拦截器处理
  } finally {
    pwdSaving.value = false;
  }
}

// ── 头像上传 ─────────────────────────────────────────────
const uploadRef = ref<UploadInstance>();
const selectedFile = ref<File | null>(null);
const previewUrl = ref("");
const avatarUploading = ref(false);
const avatarUrl = ref("");

function handleFileChange(_file: UploadRawFile) {
  selectedFile.value = _file;
  previewUrl.value = URL.createObjectURL(_file);
}

function cancelAvatar() {
  selectedFile.value = null;
  previewUrl.value = "";
}

async function handleUploadAvatar() {
  if (!selectedFile.value) return;

  avatarUploading.value = true;
  try {
    const res: any = await uploadAvatar(selectedFile.value);
    avatarUrl.value = res.url;
    if (authStore.userInfo) {
      authStore.userInfo.avatar = res.url;
    }
    ElMessage.success("头像上传成功");
    selectedFile.value = null;
    previewUrl.value = "";
  } catch {
    // 错误已由拦截器处理
  } finally {
    avatarUploading.value = false;
  }
}

// ── 初始化 ───────────────────────────────────────────────
onMounted(() => {
  loadProfile();
  avatarUrl.value = authStore.userInfo?.avatar || "";
});
</script>

<style scoped>
.profile-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 24px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.profile-form {
  max-width: 480px;
  margin-top: 16px;
}

.avatar-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 24px 0;
}

.avatar-preview {
  text-align: center;
}

.avatar-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.avatar-new-preview {
  text-align: center;
}

.avatar-new-preview p {
  margin-bottom: 12px;
  font-size: 14px;
  color: #606266;
}

.avatar-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}
</style>