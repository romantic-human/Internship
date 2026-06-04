<template>
  <Layout v-if="route.meta.layout !== false" />
  <router-view v-else />
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import Layout from "@/layout/Layout.vue";

const route = useRoute();
</script>

<style>
/* ── 暗色模式定制（覆盖 Element Plus 默认暗色变量） ──────── */
html.dark {
  /* 主背景色 */
  --el-bg-color: #1a1b23;
  --el-bg-color-overlay: #22232d;
  --el-bg-color-page: #14151c;

  /* 卡片/面板 */
  --el-fill-color: #22232d;
  --el-fill-color-light: #2a2b36;
  --el-fill-color-lighter: #323340;
  --el-fill-color-blank: #1e1f28;
  --el-fill-color-dark: #181921;

  /* 边框 */
  --el-border-color: #333440;
  --el-border-color-light: #2a2b36;
  --el-border-color-lighter: #22232d;
  --el-border-color-extra-light: #1a1b23;

  /* 文字 */
  --el-text-color-primary: #e0e2e8;
  --el-text-color-regular: #c8cad0;
  --el-text-color-secondary: #a0a2a8;
  --el-text-color-placeholder: #787a80;
  --el-text-color-disabled: #585a60;

  /* 遮罩 */
  --el-mask-color: rgba(0, 0, 0, 0.6);

  /* 菜单/导航 */
  --el-menu-bg-color: #1a1b23;
  --el-menu-text-color: #c8cad0;
  --el-menu-hover-bg-color: #2a2b36;
  --el-menu-active-color: #409eff;

  /* 头部 */
  --el-header-bg-color: #1e1f28;
}

/* 侧边栏暗色 */
html.dark .layout-aside { background: #16171e !important; }
html.dark .layout-aside .el-menu { background: #16171e !important; }
html.dark .layout-aside .logo { background: #121318 !important; }

/* 表格暗色优化 */
html.dark .el-table {
  --el-table-border-color: #2a2b36;
  --el-table-header-bg-color: #1a1b23;
  --el-table-row-hover-bg-color: #22232d;
  --el-table-text-color: #e0e2e8;
}
html.dark .el-table__body td { color: #e0e2e8; }
html.dark .el-pagination button, 
html.dark .el-pagination span,
html.dark .el-pagination .el-input__inner { color: #e0e2e8; }
html.dark .el-tag { --el-tag-text-color: #e0e2e8; }
html.dark .el-input-number .el-input__inner { color: #e0e2e8; }
</style>