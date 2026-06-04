<template>
  <el-dialog :model-value="visible" :title="isEdit ? '编辑配置' : '新增配置'" width="500px" @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="配置名称" prop="config_name">
        <el-input v-model="form.config_name" placeholder="如 系统标题" />
      </el-form-item>
      <el-form-item label="配置键" prop="config_key">
        <el-input v-model="form.config_key" placeholder="如 system.title" />
      </el-form-item>
      <el-form-item label="配置值" prop="config_value">
        <el-input v-model="form.config_value" type="textarea" :rows="3" placeholder="配置值" />
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="form.config_type" style="width:100%">
          <el-option label="字符串" :value="0" /><el-option label="数字" :value="1" />
          <el-option label="布尔" :value="2" /><el-option label="JSON" :value="3" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" placeholder="备注" type="textarea" :rows="2" />
      </el-form-item>
      <el-form-item label="排序号">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>
      <el-form-item label="启用状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { createConfig, updateConfig, type ConfigItem } from "@/api/config";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{ visible: boolean; formData: Partial<ConfigItem> | null }>();
const emit = defineEmits<{ close: []; success: [] }>();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const form = ref<Partial<ConfigItem>>({ config_name: "", config_key: "", config_value: "", config_type: 0, remark: "", sort_order: 0, status: 1 });
const rules = { config_name: [{ required: true, message: "请输入配置名称", trigger: "blur" }], config_key: [{ required: true, message: "请输入配置键", trigger: "blur" }], config_value: [{ required: true, message: "请输入配置值", trigger: "blur" }] };
const isEdit = computed(() => !!props.formData?.id);
watch(() => props.formData, (val) => {
  if (val) { Object.assign(form.value, { config_name: val.config_name || "", config_key: val.config_key || "", config_value: val.config_value || "", config_type: val.config_type ?? 0, remark: val.remark || "", sort_order: val.sort_order ?? 0, status: val.status ?? 1 }); }
  else { form.value = { config_name: "", config_key: "", config_value: "", config_type: 0, remark: "", sort_order: 0, status: 1 }; }
}, { immediate: true });
function handleClose() { emit("close"); }
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return; submitting.value = true;
  try {
    if (isEdit.value) { await updateConfig(props.formData!.id!, form.value); ElMessage.success("更新成功"); }
    else { await createConfig(form.value); ElMessage.success("新增成功"); }
    emit("success"); emit("close");
  } finally { submitting.value = false; }
}
</script>