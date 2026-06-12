<template>
  <el-dialog :model-value="visible" :title="isEdit ? '编辑权限' : '新增权限'" width="450px" @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="权限名称" prop="permission_name">
        <el-input v-model="form.permission_name" placeholder="如 新增用户" />
      </el-form-item>
      <el-form-item label="权限标识" prop="permission_key">
        <el-input v-model="form.permission_key" placeholder="如 user:add" />
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
import { createPermission, updatePermission, type PermissionItem } from "@/api/permission";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{ visible: boolean; formData: Partial<PermissionItem> | null }>();
const emit = defineEmits<{ close: []; success: [] }>();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const form = ref<Partial<PermissionItem>>({ permission_name: "", permission_key: "", sort_order: 0, status: 1 });
const rules = { permission_name: [{ required: true, message: "请输入权限名称", trigger: "blur" }], permission_key: [{ required: true, message: "请输入权限标识", trigger: "blur" }] };
const isEdit = computed(() => !!props.formData?.id);
watch(() => props.formData, (val: Partial<PermissionItem> | null) => {
  if (val) { Object.assign(form.value, { permission_name: val.permission_name || "", permission_key: val.permission_key || "", sort_order: val.sort_order ?? 0, status: val.status ?? 1 }); }
  else { form.value = { permission_name: "", permission_key: "", sort_order: 0, status: 1 }; }
}, { immediate: true });
function handleClose() { emit("close"); }
async function handleSubmit() {
  try { await formRef.value?.validate(); } catch { return; }
  submitting.value = true;
  try {
    if (isEdit.value) { await updatePermission(props.formData!.id!, form.value); ElMessage.success("更新成功"); }
    else { await createPermission(form.value); ElMessage.success("新增成功"); }
    emit("success"); emit("close");
  } finally { submitting.value = false; }
}
</script>