<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑成绩' : '新增成绩'"
    width="500px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="学生" prop="student">
        <el-select
          v-model="form.student"
          filterable
          remote
          :remote-method="searchStudents"
          :loading="studentLoading"
          placeholder="搜索学生姓名/学号"
          style="width:100%"
          :disabled="isEdit"
        >
          <el-option
            v-for="s in studentOptions"
            :key="s.id"
            :label="`${s.student_no} - ${s.name}`"
            :value="s.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="课程名称" prop="course_name">
        <el-input v-model="form.course_name" placeholder="请输入课程名称" />
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="成绩" prop="score">
            <el-input-number v-model="form.score" :min="0" :max="100" :precision="2" style="width:100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="学分" prop="credit">
            <el-input-number v-model="form.credit" :min="0" :max="10" :precision="1" style="width:100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="学期" prop="semester">
        <el-input v-model="form.semester" placeholder="如 2025-2026-1" />
      </el-form-item>
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
import { ref, computed, watch, onMounted } from "vue";
import { createScore, updateScore, getStudentList, type ScoreRecord, type StudentRecord } from "@/api/student";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: Partial<ScoreRecord> | null;
  studentId?: number;
}>();

const emit = defineEmits<{ close: []; success: [] }>();

const formRef = ref<FormInstance>();
const submitting = ref(false);
const isEdit = computed(() => !!props.formData?.id);

const form = ref({
  student: 0,
  course_name: "",
  score: 0,
  credit: null as number | null,
  semester: "",
  remark: "",
});

const rules = {
  student: [{ required: true, message: "请选择学生", trigger: "change" }],
  course_name: [{ required: true, message: "请输入课程名称", trigger: "blur" }],
  score: [{ required: true, message: "请输入成绩", trigger: "blur" }],
  semester: [{ required: true, message: "请输入学期", trigger: "blur" }],
};

// 学生搜索
const studentOptions = ref<StudentRecord[]>([]);
const studentLoading = ref(false);

async function searchStudents(query: string) {
  if (!query) return;
  studentLoading.value = true;
  try {
    // 同时按姓名和学号搜索
    const [byName, byNo] = await Promise.all([
      getStudentList({ page: 1, pageSize: 20, name: query }),
      getStudentList({ page: 1, pageSize: 20, student_no: query }),
    ]);
    // 合并去重
    const map = new Map<number, StudentRecord>();
    [...byName.records, ...byNo.records].forEach(s => map.set(s.id, s));
    studentOptions.value = Array.from(map.values());
  } finally {
    studentLoading.value = false;
  }
}

// 初始加载：加载默认学生列表
onMounted(async () => {
  studentLoading.value = true;
  try {
    const res = await getStudentList({ page: 1, pageSize: 100 });
    studentOptions.value = res.records;
  } finally {
    studentLoading.value = false;
  }
});

watch(
  () => props.formData,
  (val) => {
    if (val) {
      form.value = {
        student: val.student || 0,
        course_name: val.course_name || "",
        score: val.score ?? 0,
        credit: val.credit ?? null,
        semester: val.semester || "",
        remark: val.remark || "",
      };
    } else {
      form.value = {
        student: props.studentId || 0,
        course_name: "",
        score: 0,
        credit: null,
        semester: "",
        remark: "",
      };
    }
  },
  { immediate: true },
);

function handleClose() {
  emit("close");
}

async function handleSubmit() {
  try { await formRef.value?.validate(); } catch { return; }
  submitting.value = true;
  try {
    const data = {
      student: form.value.student,
      course_name: form.value.course_name,
      score: form.value.score,
      credit: form.value.credit,
      semester: form.value.semester,
      remark: form.value.remark,
    };
    if (isEdit.value) {
      await updateScore(props.formData!.id!, data);
      ElMessage.success("更新成功");
    } else {
      await createScore(data);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>
