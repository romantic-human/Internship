<template>
  <el-dialog
    :model-value="visible"
    title="绑定菜单"
    width="500px"
    @close="handleClose"
  >
    <el-tree
      ref="treeRef"
      :data="menuTree"
      show-checkbox
      node-key="id"
      :props="{ label: 'menu_name', children: 'children' }"
      :default-checked-keys="checkedKeys"
    />
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { getMenuOptions } from "@/api/menu";
import { getPermissionMenus, bindPermissionMenus } from "@/api/permission";
import { ElMessage } from "element-plus";
import type { ElTree } from "element-plus";

const props = defineProps<{
  visible: boolean;
  permissionId: number;
}>();

const emit = defineEmits<{
  close: [];
  success: [];
}>();

const treeRef = ref<InstanceType<typeof ElTree>>();
const submitting = ref(false);
const menuTree = ref<any[]>([]);
const checkedKeys = ref<number[]>([]);

watch(
  () => props.visible,
  async (v) => {
    if (v && props.permissionId) {
      const [menus, bound] = await Promise.all([
        getMenuOptions(),
        getPermissionMenus(props.permissionId),
      ]);
      menuTree.value = menus as any[];
      checkedKeys.value = (bound as number[]) ?? [];
    }
  },
);

function handleClose() {
  emit("close");
}

async function handleSubmit() {
  const checked = treeRef.value?.getCheckedKeys() as number[];
  const halfChecked = treeRef.value?.getHalfCheckedKeys() as number[];
  const allIds = [...checked, ...halfChecked];
  submitting.value = true;
  try {
    await bindPermissionMenus(props.permissionId, allIds);
    ElMessage.success("绑定成功");
    emit("success");
    emit("close");
  } finally {
    submitting.value = false;
  }
}
</script>
