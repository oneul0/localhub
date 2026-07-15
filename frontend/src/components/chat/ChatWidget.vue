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
        <div v-for="(message, index) in messages" :key="index" :class="['msg', message.role]">
          <div>{{ message.text }}</div>
          <div v-if="message.relatedPlaces?.length" class="related-places">
            <div v-for="place in message.relatedPlaces" :key="place.contentid" class="related-place">
              • {{ place.title || place.contentid }}
            </div>
          </div>
        </div>
      </div>
      <div class="quick-replies">
        <button @click="sendQuick('부산 관광지 추천해줘')">관광지 추천</button>
        <button @click="sendQuick('부산 축제 일정 알려줘')">축제 일정</button>
        <button @click="sendQuick('부산 대표 숙소 위치 알려줘')">숙소 위치</button>
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
import { sendChatMessage } from '../../api/chatbot'

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

async function sendChat() {
  const text = inputText.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', text })
  inputText.value = ''

  try {
    const response = await sendChatMessage(text)
    messages.value.push({ role: 'bot', text: response.answer, relatedPlaces: response.related_places || [] })
  } catch (error) {
    console.error('챗봇 응답 실패:', error)
    messages.value.push({ role: 'bot', text: '챗봇 응답을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.' })
  }
}
</script>
