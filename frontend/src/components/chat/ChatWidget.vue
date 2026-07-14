<template>
  <div>
    <button class="chat-fab" @click="toggleChat" aria-label="챗봇 열기">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 5h16a1 1 0 011 1v10a1 1 0 01-1 1H9l-5 4v-4H4a1 1 0 01-1-1V6a1 1 0 011-1z" fill="#fff" /></svg>
    </button>
    <div class="chat-panel" :class="{ active: isOpen }">
      <div class="chat-head">
        <strong>LocalHub 챗봇</strong>
        <button @click="toggleChat">✕</button>
      </div>
      <div class="chat-body">
        <div v-for="(message, index) in messages" :key="index" :class="['msg', message.role]">{{ message.text }}</div>
      </div>
      <div class="quick-replies">
        <button @click="sendQuick('부산 관광지 추천해줘')">관광지 추천</button>
        <button @click="sendQuick('이번 축제 일정 알려줘')">축제 일정</button>
        <button @click="sendQuick('맛집 위치 알려줘')">맛집 위치</button>
      </div>
      <div class="chat-input">
        <input v-model="inputText" type="text" placeholder="궁금한 지역 정보를 물어보세요" @keydown.enter="sendChat" />
        <button @click="sendChat">→</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { places } from '../../data/mockData'

const isOpen = ref(false)
const inputText = ref('')
const messages = ref([{ role: 'bot', text: '안녕하세요! LocalHub 챗봇이에요 🐬 부산의 관광지, 맛집, 축제 일정이나 게시글을 물어보세요.' }])

function toggleChat() {
  isOpen.value = !isOpen.value
}

function sendQuick(text) {
  inputText.value = text
  sendChat()
}

function sendChat() {
  const text = inputText.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  inputText.value = ''
  setTimeout(() => {
    messages.value.push({ role: 'bot', text: botReply(text) })
  }, 300)
}

function botReply(text) {
  const t = text.toLowerCase()
  if (t.includes('축제') || t.includes('행사') || t.includes('일정')) {
    return `다가오는 부산 축제·행사예요:\n${places.filter((p) => p.cat === '축제·행사').map((p) => `• ${p.name} — ${p.desc}`).join('\n')}`
  }
  if (t.includes('맛집') || t.includes('음식')) {
    return `부산 맛집 추천이에요:\n${places.filter((p) => p.cat === '맛집').map((p) => `• ${p.name} — ${p.desc}`).join('\n')}`
  }
  if (t.includes('관광') || t.includes('추천') || t.includes('여행')) {
    return `부산 관광지 추천이에요:\n${places.filter((p) => p.cat === '관광지').map((p) => `• ${p.name} — ${p.desc}`).join('\n')}`
  }
  return '아직 배우는 중이에요 🙏 "관광지 추천", "축제 일정", "맛집 위치", "게시글 검색" 같은 질문을 해보세요.'
}
</script>
