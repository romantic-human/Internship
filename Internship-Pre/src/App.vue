<template>
  <Layout v-if="route.meta.layout !== false" />
  <router-view v-else />
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import Layout from "@/layout/Layout.vue";

const route = useRoute();
</script>
