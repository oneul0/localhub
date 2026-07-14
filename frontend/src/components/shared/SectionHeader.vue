<template>
  <div class="section-head">
    <h2>{{ title }}</h2>
    <router-link v-if="to" class="see-all" :to="to">{{ linkText }}</router-link>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  to: { type: String, default: '' },
  linkText: { type: String, default: '전체보기 →' }
})
</script>
