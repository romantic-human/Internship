<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑角色' : '新增角色'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="角色名称" prop="role_name">
        <el-input v-model="form.role_name" placeholder="请输入角色名称" />
      </el-form-item>
      <el-form-item label="角色标识" prop="role_key">
        <el-input v-model="form.role_key" placeholder="如 admin、user" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="排序号" prop="role_sort">
        <el-input-number v-model="form.role_sort" :min="0" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注信息" />
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
import { createRole, updateRole, type RoleRecord } from "@/api/role";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: Partial<RoleRecord> | null;
}>();

const emit = defineEmits<{ close: []; success: [] }>();

const formRef = ref<FormInstance>();
const submitting = ref(false);

const form = ref<Partial<RoleRecord>>({
  role_name: "",
  role_key: "",
  role_sort: 0,
  status: 1,
  remark: "",
});

const rules = {
  role_name: [{ required: true, message: "请输入角色名称", trigger: "blur" }],
  role_key: [{ required: true, message: "请输入角色标识", trigger: "blur" }],
};

const isEdit = computed(() => !!props.formData?.id);

watch(
  () => props.formData,
  (val) => {
    if (val) {
      form.value = {
        role_name: val.role_name || "",
        role_key: val.role_key || "",
        role_sort: val.role_sort ?? 0,
        status: val.status ?? 1,
        remark: val.remark || "",
      };
    } else {
      form.value = { role_name: "", role_key: "", role_sort: 0, status: 1, remark: "" };
    }
  },
  { immediate: true },
);

function handleClose() {
  emit("close");
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  submitting.value = true;
  try {
    if (isEdit.value) {
      await updateRole(props.formData!.id!, form.value);
      ElMessage.success("更新成功");
    } else {
      await createRole(form.value);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>