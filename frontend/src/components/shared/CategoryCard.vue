<template>
  <router-link class="cat-card" :to="to">
    <div class="cat-icon" :style="{ background: iconBg }">{{ icon }}</div>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </router-link>
</template>

<script setup>
defineProps({
  to: { type: String, required: true },
  icon: { type: String, required: true },
  iconBg: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true }
})
</script>
