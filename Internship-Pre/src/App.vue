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
