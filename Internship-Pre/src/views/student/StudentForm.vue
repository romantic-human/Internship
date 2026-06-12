<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑学生' : '新增学生'"
    width="600px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学号" prop="student_no">
            <el-input v-model="form.student_no" placeholder="请输入学号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="性别" prop="gender">
            <el-select v-model="form.gender" style="width:100%">
              <el-option label="未知" :value="0" />
              <el-option label="男" :value="1" />
              <el-option label="女" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="入学年份" prop="enrollment_year">
            <el-input-number v-model="form.enrollment_year" :min="2000" :max="2030" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="班级" prop="class_name">
            <el-input v-model="form.class_name" placeholder="请输入班级" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="专业" prop="major">
            <el-input v-model="form.major" placeholder="请输入专业" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="学院" prop="college">
            <el-input v-model="form.college" placeholder="请输入学院" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="状态" prop="status">
            <el-select v-model="form.status" style="width:100%">
              <el-option label="休学" :value="0" />
              <el-option label="在读" :value="1" />
              <el-option label="毕业" :value="2" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="备注信息" />
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
import { createStudent, updateStudent, type StudentRecord } from "@/api/student";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: Partial<StudentRecord> | null;
}>();

const emit = defineEmits<{ close: []; success: [] }>();

const formRef = ref<FormInstance>();
const submitting = ref(false);
const isEdit = computed(() => !!props.formData?.id);

const form = ref<Partial<StudentRecord>>({
  student_no: "",
  name: "",
  gender: 0,
  class_name: "",
  major: "",
  college: "",
  phone: "",
  email: "",
  enrollment_year: new Date().getFullYear(),
  status: 1,
  remark: "",
});

const rules = {
  student_no: [{ required: true, message: "请输入学号", trigger: "blur" }],
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
};

watch(
  () => props.formData,
  (val) => {
    if (val) {
      form.value = { ...val };
    } else {
      form.value = {
        student_no: "", name: "", gender: 0, class_name: "",
        major: "", college: "", phone: "", email: "",
        enrollment_year: new Date().getFullYear(), status: 1, remark: "",
      };
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
      await updateStudent(props.formData!.id!, form.value);
      ElMessage.success("更新成功");
    } else {
      await createStudent(form.value);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>
