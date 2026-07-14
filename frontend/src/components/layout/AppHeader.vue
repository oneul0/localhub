<template>
  <header class="app-header">
    <div class="brand">LocalHub</div>
    <nav>
      <router-link to="/">홈</router-link>
      <router-link to="/places">관광지</router-link>
      <router-link to="/board">게시판</router-link>
      <router-link to="/chatbot">챗봇</router-link>
    </nav>
    <button class="theme-btn" @click="store.toggleTheme">{{ store.theme === 'light' ? '다크모드' : '라이트모드' }}</button>
  </header>
</template>

<script setup>
import { useAppStore } from '../../stores/app'
const store = useAppStore()
</script>
