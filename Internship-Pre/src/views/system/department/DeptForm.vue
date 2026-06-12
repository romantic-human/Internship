<template>
  <el-dialog :model-value="visible" :title="isEdit ? '编辑部门' : '新增部门'" width="500px" @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="上级部门" prop="parent_id">
        <el-tree-select v-model="form.parent_id" :data="treeOptions"
          :props="{ label: 'dept_name', value: 'id' }" placeholder="顶级部门" clearable check-strictly style="width:100%" />
      </el-form-item>
      <el-form-item label="部门名称" prop="dept_name">
        <el-input v-model="form.dept_name" placeholder="请输入部门名称" />
      </el-form-item>
      <el-form-item label="负责人">
        <el-input v-model="form.leader" placeholder="请输入负责人" />
      </el-form-item>
      <el-form-item label="联系电话">
        <el-input v-model="form.phone" placeholder="请输入联系电话" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
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
import { createDepartment, updateDepartment, getDepartmentTree, type DeptItem } from "@/api/department";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{ visible: boolean; formData: Partial<DeptItem> | null }>();
const emit = defineEmits<{ close: []; success: [] }>();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const treeOptions = ref<DeptItem[]>([]);
const form = ref<Partial<DeptItem> & { parent_id: number | null }>({ parent_id: null, dept_name: "", leader: "", phone: "", email: "", sort_order: 0, status: 1 });
const rules = { dept_name: [{ required: true, message: "请输入部门名称", trigger: "blur" }] };
const isEdit = computed(() => !!props.formData?.id);

watch(() => props.visible, async (v) => { if (v) treeOptions.value = await getDepartmentTree(); }, { immediate: true });
watch(() => props.formData, (val) => {
  if (val) { Object.assign(form.value, { parent_id: val.parent_id || null, dept_name: val.dept_name || "", leader: val.leader || "", phone: val.phone || "", email: val.email || "", sort_order: val.sort_order ?? 0, status: val.status ?? 1 }); }
  else { form.value = { parent_id: null, dept_name: "", leader: "", phone: "", email: "", sort_order: 0, status: 1 }; }
}, { immediate: true });

function handleClose() { emit("close"); }
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return; submitting.value = true;
  try {
    const payload = { ...form.value, parent_id: form.value.parent_id || 0 };
    if (isEdit.value) { await updateDepartment(props.formData!.id!, payload); ElMessage.success("更新成功"); }
    else { await createDepartment(payload); ElMessage.success("新增成功"); }
    emit("success"); emit("close");
  } finally { submitting.value = false; }
}
</script>
