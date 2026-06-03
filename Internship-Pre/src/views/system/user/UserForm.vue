<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑用户' : '新增用户'"
    width="550px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="form.nickname" placeholder="请输入昵称" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="手机号" prop="telephone">
        <el-input v-model="form.telephone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="状态">
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
import { createUser, updateUser } from "@/api/user";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: any;
}>();

const emit = defineEmits<{ close: []; success: [] }>();

const formRef = ref<FormInstance>();
const submitting = ref(false);

const form = ref({
  username: "",
  nickname: "",
  email: "",
  telephone: "",
  status: 1,
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  email: [{ type: "email", message: "请输入正确邮箱", trigger: "blur" }],
};

const isEdit = computed(() => !!props.formData?.id);

watch(
  () => props.formData,
  (val) => {
    if (val) {
      form.value = {
        username: val.username || "",
        nickname: val.nickname || "",
        email: val.email || "",
        telephone: val.telephone || "",
        status: val.status ?? 1,
      };
    } else {
      form.value = { username: "", nickname: "", email: "", telephone: "", status: 1 };
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
      await updateUser(props.formData.id, form.value);
      ElMessage.success("更新成功");
    } else {
      await createUser(form.value);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>