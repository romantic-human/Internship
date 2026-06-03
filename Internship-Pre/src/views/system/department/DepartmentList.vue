<template>
  <div class="department-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-button type="primary" :icon="Plus" @click="handleAdd(null)">新增根部门</el-button>
      <el-button :icon="Refresh" @click="loadTree">刷新</el-button>
    </el-card>

    <!-- 部门树表格 -->
    <el-card class="tree-card">
      <el-table
        :data="treeData"
        row-key="id"
        border
        default-expand-all
        v-loading="loading"
      >
        <el-table-column prop="dept_name" label="部门名称" min-width="200" />
        <el-table-column prop="leader" label="负责人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleAdd(row)">新增子部门</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑部门' : (parentDept ? '新增子部门' : '新增根部门')"
      width="520px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item v-if="parentDept" label="上级部门">
          <el-input :model-value="parentDept.dept_name" disabled />
        </el-form-item>
        <el-form-item label="部门名称" prop="dept_name">
          <el-input v-model="form.dept_name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="负责人" prop="leader">
          <el-input v-model="form.leader" placeholder="请输入负责人" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="排序号" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :step="10" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { Plus, Refresh } from "@element-plus/icons-vue";
import {
  getDepartmentTree,
  createDepartment,
  updateDepartment,
  deleteDepartment,
} from "@/api/department";

const loading = ref(false);
const treeData = ref<any[]>([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const saving = ref(false);
const formRef = ref<FormInstance>();
const parentDept = ref<any>(null);
const editId = ref<number | null>(null);

const form = reactive({
  dept_name: "",
  leader: "",
  phone: "",
  email: "",
  sort_order: 0,
  status: 1,
  parent_id: null as number | null,
});

const rules: FormRules = {
  dept_name: [{ required: true, message: "请输入部门名称", trigger: "blur" }],
  email: [{ type: "email", message: "请输入正确的邮箱格式", trigger: "blur" }],
};

async function loadTree() {
  loading.value = true;
  try {
    const data = await getDepartmentTree();
    treeData.value = data || [];
  } catch { /* handled */ }
  finally { loading.value = false; }
}

function resetForm() {
  form.dept_name = "";
  form.leader = "";
  form.phone = "";
  form.email = "";
  form.sort_order = 0;
  form.status = 1;
  form.parent_id = null;
}

function handleAdd(parent: any | null) {
  isEdit.value = false;
  editId.value = null;
  parentDept.value = parent;
  resetForm();
  if (parent) form.parent_id = parent.id;
  dialogVisible.value = true;
}

function handleEdit(row: any) {
  isEdit.value = true;
  editId.value = row.id;
  parentDept.value = null;
  form.dept_name = row.dept_name;
  form.leader = row.leader || "";
  form.phone = row.phone || "";
  form.email = row.email || "";
  form.sort_order = row.sort_order;
  form.status = row.status;
  form.parent_id = null;
  dialogVisible.value = true;
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除部门「${row.dept_name}」吗？若有子部门也会一并删除。`,
      "确认删除",
      { type: "warning" },
    );
  } catch { return; }

  try {
    await deleteDepartment(row.id);
    ElMessage.success("删除成功");
    loadTree();
  } catch { /* handled */ }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const payload: any = {
      dept_name: form.dept_name,
      leader: form.leader,
      phone: form.phone,
      email: form.email,
      sort_order: form.sort_order,
      status: form.status,
    };

    if (isEdit.value && editId.value) {
      await updateDepartment(editId.value, payload);
      ElMessage.success("更新成功");
    } else {
      if (form.parent_id) payload.parent_id = form.parent_id;
      await createDepartment(payload);
      ElMessage.success("新增成功");
    }

    dialogVisible.value = false;
    loadTree();
  } catch { /* handled */ }
  finally { saving.value = false; }
}

onMounted(loadTree);
</script>

<style scoped>
.department-container {
  padding: 16px;
}
.toolbar-card {
  margin-bottom: 16px;
}
</style>
