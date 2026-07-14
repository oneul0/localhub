<template>
  <section class="view-shell">
    <router-link class="back-link" to="/board">← 게시판으로</router-link>
    <div class="detail-card" v-if="post">
      <h2>{{ post.title }}</h2>
      <div class="detail-meta"><span class="mono">{{ formatDate(post.created_at) }}</span><span>·</span><span>👁 조회수 {{ post.view_count }}</span></div>
      <div class="detail-body">{{ post.content }}</div>
      <div class="detail-actions">
        <button class="btn btn-outline btn-sm" @click="requestPassword('edit')">수정</button>
        <button class="btn btn-primary btn-sm" @click="requestPassword('delete')">삭제</button>
      </div>
    </div>
    <div v-else class="empty-state">존재하지 않는 게시글입니다.</div>

    <div class="overlay" :class="{ active: showModal }">
      <div class="modal">
        <h3>비밀번호 확인</h3>
        <p>게시글 작성 시 등록한 수정용 비밀번호를 입력해주세요.</p>
        <input v-model="passwordInput" type="password" placeholder="수정용 비밀번호" />
        <div v-if="passwordError" class="modal-error" style="display:block">비밀번호가 일치하지 않습니다.</div>
        <div class="modal-actions">
          <button class="btn btn-outline btn-sm" @click="closeModal">취소</button>
          <button class="btn btn-primary btn-sm" @click="confirmPassword">확인</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deletePost, getPostById, verifyPostPassword } from '../api/posts'

const props = defineProps({ id: { type: [String, Number], required: true } })
const route = useRoute()
const router = useRouter()
const post = ref(null)
const passwordInput = ref('')
const passwordError = ref(false)
const showModal = ref(false)
const pendingAction = ref(null)

async function loadPost() {
  try {
    post.value = await getPostById(props.id || route.params.id)
  } catch (error) {
    console.error('게시글 상세 조회 실패:', error)
    post.value = null
  }
}

function requestPassword(type) {
  pendingAction.value = type
  passwordInput.value = ''
  passwordError.value = false
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  pendingAction.value = null
}

function formatDate(value) {
  return value ? value.slice(0, 10) : ''
}

async function confirmPassword() {
  if (!post.value) return
  try {
    if (pendingAction.value === 'edit') {
      await verifyPostPassword(post.value.post_id, passwordInput.value)
      closeModal()
      await router.push(`/board/${post.value.post_id}/edit`)
      return
    }

    await deletePost(post.value.post_id, passwordInput.value)
    closeModal()
    await router.push('/board')
  } catch (error) {
    passwordError.value = true
  }
}

onMounted(() => {
  loadPost()
})
</script>
