<template>
  <router-view v-if="route.meta.layout === false" v-slot="{ Component }">
    <transition name="fade-slide" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
  <Layout v-else />
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { useAppStore } from "@/store/app";
import Layout from "@/layout/Layout.vue";

const route = useRoute();
useAppStore();
</script>

<style>
html.dark {
  --el-bg-color: #1a1b23;
  --el-bg-color-overlay: #22232d;
  --el-bg-color-page: #14151c;
  --el-fill-color: #22232d;
  --el-fill-color-light: #2a2b36;
  --el-fill-color-lighter: #323340;
  --el-fill-color-blank: #1e1f28;
  --el-fill-color-dark: #181921;
  --el-border-color: #333440;
  --el-border-color-light: #2a2b36;
  --el-border-color-lighter: #22232d;
  --el-border-color-extra-light: #1a1b23;
  --el-text-color-primary: #e0e2e8;
  --el-text-color-regular: #c8cad0;
  --el-text-color-secondary: #a0a2a8;
  --el-text-color-placeholder: #787a80;
  --el-text-color-disabled: #585a60;
  --el-mask-color: rgba(0, 0, 0, 0.6);
  --el-menu-bg-color: #1a1b23;
  --el-menu-text-color: #c8cad0;
  --el-menu-hover-bg-color: #2a2b36;
  --el-menu-active-color: #409eff;
  --el-header-bg-color: #1e1f28;
}
html.dark .layout-aside { background: #16171e !important; }
html.dark .layout-aside .el-menu { background: #16171e !important; }
html.dark .layout-aside .logo { background: #121318 !important; }
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
