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
      <el-form-item label="真实姓名" prop="real_name">
        <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
      </el-form-item>
      <el-form-item label="性别" prop="gender">
        <el-select v-model="form.gender" style="width:100%">
          <el-option :value="0" label="保密" />
          <el-option :value="1" label="男" />
          <el-option :value="2" label="女" />
        </el-select>
      </el-form-item>
      <el-form-item label="所属部门" prop="department_id">
        <el-tree-select
          v-model="form.department_id"
          :data="deptOptions"
          :props="{ label: 'dept_name', children: 'children', value: 'id' }"
          placeholder="请选择部门"
          check-strictly
          clearable
          filterable
        />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="手机号" prop="telephone">
        <el-input v-model="form.telephone" placeholder="请输入手机号" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="form.role_ids" multiple style="width:100%" placeholder="请选择角色" clearable>
          <el-option v-for="r in roleOptions" :key="r.id" :label="r.role_name" :value="r.id" />
        </el-select>
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
import { ref, computed, watch, onMounted } from "vue";
import { createUser, updateUser, type UserRecord } from "@/api/user";
import { getDepartmentTree, type DeptItem } from "@/api/department";
import { getAllRoles, type RoleRecord } from "@/api/role";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: Partial<UserRecord> | null;
}>();

const emit = defineEmits<{ close: []; success: [] }>();

const formRef = ref<FormInstance>();
const submitting = ref(false);
const deptOptions = ref<DeptItem[]>([]);
const roleOptions = ref<RoleRecord[]>([]);

const form = ref({
  username: "",
  nickname: "",
  real_name: "",
  gender: 0,
  department_id: null as number | null,
  email: "",
  telephone: "",
  role_ids: [] as number[],
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
        real_name: val.real_name || "",
        gender: val.gender ?? 0,
        department_id: val.department_id ?? null,
        email: val.email || "",
        telephone: val.telephone || "",
        role_ids: val.role_ids || [],
        status: val.status ?? 1,
      };
    } else {
      form.value = {
        username: "", nickname: "", real_name: "", gender: 0,
        department_id: null, email: "", telephone: "", role_ids: [], status: 1,
      };
    }
  },
  { immediate: true },
);

onMounted(async () => {
  deptOptions.value = await getDepartmentTree();
  roleOptions.value = await getAllRoles();
});

function handleClose() {
  emit("close");
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;
  submitting.value = true;
  try {
    if (isEdit.value) {
      await updateUser(props.formData!.id!, form.value);
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