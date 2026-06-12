<template>
  <div class="config-panel-page">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:16px;font-weight:bold">系统配置</span>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
        </div>
      </template>

      <div class="config-sections">
        <!-- 品牌与标识 -->
        <div class="config-section">
          <h3 class="section-title">品牌与标识</h3>
          <el-form label-width="100px">
            <el-form-item label="系统名称">
              <el-input v-model="form['system.name']" placeholder="请输入系统名称" style="max-width:360px" />
            </el-form-item>
            <el-form-item label="系统 Logo">
              <el-upload
                class="logo-uploader"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                accept=".jpg,.jpeg,.png,.webp"
                :on-change="handleLogoChange"
              >
                <img v-if="form['system.logo']" :src="form['system.logo']" class="logo-preview" />
                <el-icon v-else class="logo-placeholder"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">推荐尺寸：128 × 128px，支持 JPG/PNG/WebP，不超过 2MB</div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 日志与审计 -->
        <div class="config-section">
          <h3 class="section-title">日志与审计</h3>
          <el-form label-width="120px">
            <el-form-item label="日志分析">
              <el-switch
                :model-value="form['log.enabled'] === '1'"
                @change="(val: boolean) => form['log.enabled'] = val ? '1' : '0'"
              />
              <span class="switch-tip">开启后将记录所有操作日志</span>
            </el-form-item>
            <el-form-item label="日志保留天数">
              <el-input-number
                :model-value="Number(form['log.retention_days'])"
                @update:model-value="(val: number) => form['log.retention_days'] = String(val)"
                :min="1"
                :max="365"
                :step="1"
              />
              <span class="switch-tip" style="margin-left:12px">天</span>
            </el-form-item>
            <el-form-item label="异常告警">
              <el-switch
                :model-value="form['log.alert_enabled'] === '1'"
                @change="(val: boolean) => form['log.alert_enabled'] = val ? '1' : '0'"
              />
              <span class="switch-tip">开启后系统异常时自动告警</span>
            </el-form-item>
          </el-form>
        </div>

        <!-- 安全级别 -->
        <div class="config-section">
          <h3 class="section-title">安全级别</h3>
          <el-form label-width="120px">
            <el-form-item label="安全级别">
              <el-select v-model="form['security.level']" style="width:200px">
                <el-option label="低" value="低" />
                <el-option label="中" value="中" />
                <el-option label="高" value="高" />
              </el-select>
            </el-form-item>
            <el-form-item label="双因素认证">
              <el-switch
                :model-value="form['security.two_factor'] === '1'"
                @change="(val: boolean) => form['security.two_factor'] = val ? '1' : '0'"
              />
              <span class="switch-tip">开启后用户登录需二次验证</span>
            </el-form-item>
            <el-form-item label="密码策略">
              <el-input
                v-model="form['security.password_policy']"
                placeholder="如：至少8位，包含数字与大小写字母"
                style="max-width:400px"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { getPanelConfig, savePanelConfig, uploadImage, type PanelConfig } from "@/api/configPanel";
import { ElMessage } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import type { UploadFile } from "element-plus";

const loading = ref(false);
const saving = ref(false);

const form = reactive<Record<string, string>>({
  "system.name": "",
  "system.logo": "",
  "log.enabled": "1",
  "log.retention_days": "90",
  "log.alert_enabled": "1",
  "security.level": "高",
  "security.two_factor": "1",
  "security.password_policy": "",
});

async function fetchConfig() {
  loading.value = true;
  try {
    const data = await getPanelConfig();
    Object.keys(form).forEach((key) => {
      if (data[key as keyof PanelConfig] !== undefined) {
        form[key] = data[key as keyof PanelConfig];
      }
    });
  } finally {
    loading.value = false;
  }
}

async function handleSave() {
  saving.value = true;
  try {
    await savePanelConfig(form);
    ElMessage.success("配置保存成功");
  } catch {
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
}

async function handleLogoChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return;
  const raw = uploadFile.raw;
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
  if (!allowedTypes.includes(raw.type)) {
    ElMessage.error("仅允许上传 JPG/PNG/WebP 格式的图片");
    return;
  }
  if (raw.size > 2 * 1024 * 1024) {
    ElMessage.error("图片大小不能超过 2MB");
    return;
  }
  try {
    const res = await uploadImage(raw);
    form["system.logo"] = res.url;
    ElMessage.success("Logo 上传成功");
  } catch {
    ElMessage.error("Logo 上传失败");
  }
}

onMounted(fetchConfig);
</script>

<style scoped>
.config-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}
.config-section {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fafafa;
}
.config-section:first-child {
  grid-column: 1 / -1;
}
.section-title {
  margin: 0 0 16px 0;
  font-size: 15px;
  color: #303133;
  border-left: 3px solid #409eff;
  padding-left: 10px;
}
.switch-tip {
  color: #909399;
  font-size: 13px;
  margin-left: 12px;
}
.logo-uploader {
  display: inline-block;
}
.logo-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  overflow: hidden;
  width: 128px;
  height: 128px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}
.logo-preview {
  width: 128px;
  height: 128px;
  object-fit: contain;
}
.logo-placeholder {
  font-size: 28px;
  color: #8c939d;
}
.upload-tip {
  margin-top: 8px;
  color: #909399;
  font-size: 12px;
}
</style>
