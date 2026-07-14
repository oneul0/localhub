<template>
  <div class="app-shell">
    <AppHeader />
    <main>
      <router-view />
    </main>
    <AppFooter />
    <ChatWidget />
  </div>
</template>

<script setup>
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import ChatWidget from './components/chat/ChatWidget.vue'
</script>
