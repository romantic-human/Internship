<template>
  <el-dialog :model-value="visible" :title="isEdit ? '编辑字典类型' : '新增字典类型'" width="500px" @close="handleClose">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="字典名称" prop="dict_name">
        <el-input v-model="form.dict_name" placeholder="如 用户性别" />
      </el-form-item>
      <el-form-item label="字典类型编码" prop="dict_type">
        <el-input v-model="form.dict_type" placeholder="如 sys_user_gender" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="备注说明" />
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
import { createDictType, updateDictType, type DictType } from "@/api/dict";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{ visible: boolean; formData: Partial<DictType> | null }>();
const emit = defineEmits<{ close: []; success: [] }>();
const formRef = ref<FormInstance>();
const submitting = ref(false);
const form = ref<Partial<DictType>>({ dict_name: "", dict_type: "", status: 1, remark: "" });
const rules = {
  dict_name: [{ required: true, message: "请输入字典名称", trigger: "blur" }],
  dict_type: [{ required: true, message: "请输入字典类型编码", trigger: "blur" }],
};
const isEdit = computed(() => !!props.formData?.id);

watch(() => props.formData, (val: Partial<DictType> | null) => {
  if (val) {
    Object.assign(form.value, {
      dict_name: val.dict_name || "",
      dict_type: val.dict_type || "",
      status: val.status ?? 1,
      remark: val.remark || "",
    });
  } else {
    form.value = { dict_name: "", dict_type: "", status: 1, remark: "" };
  }
}, { immediate: true });

function handleClose() { emit("close"); }

async function handleSubmit() {
  try { await formRef.value?.validate(); } catch { return; }
  submitting.value = true;
  try {
    if (isEdit.value) {
      await updateDictType(props.formData!.id!, form.value);
      ElMessage.success("更新成功");
    } else {
      await createDictType(form.value);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally { submitting.value = false; }
}
</script>
