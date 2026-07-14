<template>
  <div class="board-box">
    <div v-for="post in posts" :key="post.id" class="post-row" @click="$emit('select', post.id)">
      <span class="post-title">{{ post.title }}</span>
      <span class="post-views">👁 {{ post.views }}</span>
      <span class="post-date mono">{{ post.date }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({ posts: { type: Array, required: true } })
defineEmits(['select'])
</script>
