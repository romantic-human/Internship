<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑菜单' : '新增菜单'"
    width="600px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="上级菜单" prop="parent_id">
        <el-tree-select
          v-model="form.parent_id"
          :data="treeOptions"
          :props="{ label: 'menu_name', value: 'id' }"
          placeholder="顶级菜单"
          clearable
          check-strictly
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="菜单类型" prop="menu_type">
        <el-radio-group v-model="form.menu_type">
          <el-radio :value="0">目录</el-radio>
          <el-radio :value="1">菜单</el-radio>
          <el-radio :value="2">按钮</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="菜单名称" prop="menu_name">
        <el-input v-model="form.menu_name" placeholder="请输入菜单名称" />
      </el-form-item>

      <el-form-item label="图标" prop="icon" v-if="form.menu_type !== 2">
        <el-input v-model="form.icon" placeholder="Element Plus 图标名" />
      </el-form-item>

      <el-form-item label="路由路径" prop="path" v-if="form.menu_type !== 2">
        <el-input v-model="form.path" placeholder="如 /system/menu" />
      </el-form-item>

      <el-form-item label="组件路径" prop="component" v-if="form.menu_type === 1">
        <el-input v-model="form.component" placeholder="如 system/menu/MenuTree" />
      </el-form-item>

      <el-form-item label="权限标识" prop="permission" v-if="form.menu_type === 2">
        <el-input v-model="form.permission" placeholder="如 menu:add" />
      </el-form-item>

      <el-form-item label="排序号" prop="sort_order">
        <el-input-number v-model="form.sort_order" :min="0" />
      </el-form-item>

      <el-form-item label="显示状态">
        <el-switch v-model="form.visible" :active-value="1" :inactive-value="0" />
      </el-form-item>

      <el-form-item label="启用状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" />
      </el-form-item>

      <el-form-item label="外链" v-if="form.menu_type !== 2">
        <el-switch v-model="form.is_frame" :active-value="1" :inactive-value="0" />
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
import { createMenu, updateMenu } from "@/api/menu";
import { ElMessage } from "element-plus";
import type { FormInstance } from "element-plus";

const props = defineProps<{
  visible: boolean;
  formData: any;
  treeOptions: any[];
}>();

const emit = defineEmits<{
  close: [];
  success: [];
}>();

const formRef = ref<FormInstance>();
const submitting = ref(false);

const form = ref<any>({
  parent_id: null,
  menu_type: 0,
  menu_name: "",
  path: "",
  component: "",
  icon: "",
  permission: "",
  sort_order: 0,
  visible: 1,
  status: 1,
  is_frame: 0,
});

const rules = {
  menu_name: [{ required: true, message: "请输入菜单名称", trigger: "blur" }],
};

const isEdit = computed(() => !!props.formData?.id);

watch(
  () => props.formData,
  (val) => {
    if (val) {
      form.value = {
        parent_id: val.parent_id || null,
        menu_type: val.menu_type ?? 0,
        menu_name: val.menu_name || "",
        path: val.path || "",
        component: val.component || "",
        icon: val.icon || "",
        permission: val.permission || "",
        sort_order: val.sort_order ?? 0,
        visible: val.visible ?? 1,
        status: val.status ?? 1,
        is_frame: val.is_frame ?? 0,
      };
    } else {
      form.value = {
        parent_id: null,
        menu_type: 0,
        menu_name: "",
        path: "",
        component: "",
        icon: "",
        permission: "",
        sort_order: 0,
        visible: 1,
        status: 1,
        is_frame: 0,
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
    const payload = { ...form.value, parent_id: form.value.parent_id || 0 };
    if (isEdit.value) {
      await updateMenu(props.formData.id, payload);
      ElMessage.success("更新成功");
    } else {
      await createMenu(payload);
      ElMessage.success("新增成功");
    }
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>
