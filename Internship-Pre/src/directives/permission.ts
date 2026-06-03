import type { App, DirectiveBinding } from "vue";
import { useAuthStore } from "@/store/auth";

/**
 * 按钮级权限指令
 * 用法: <el-button v-permission="'user:add'">新增用户</el-button>
 */
export function setupPermissionDirective(app: App) {
  app.directive("permission", {
    mounted(el: HTMLElement, binding: DirectiveBinding) {
      const { value } = binding;
      if (!value) return;
      const authStore = useAuthStore();
      if (!authStore.hasPermission(value)) {
        el.parentNode?.removeChild(el);
      }
    },
  });
}