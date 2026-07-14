<template>
  <section class="view-shell wide-view">
    <router-link class="back-link" to="/board">← 게시판으로</router-link>
    <div class="section-head" style="margin-top: 6px;">
      <h2>{{ isEdit ? '게시글 수정' : '게시글 작성' }}</h2>
    </div>
    <div class="form-card">
      <div class="field">
        <label>제목</label>
        <input v-model="title" type="text" placeholder="제목을 입력하세요" />
      </div>
      <div class="field">
        <label>내용</label>
        <textarea v-model="body" placeholder="내용을 입력하세요"></textarea>
      </div>
      <div class="field">
        <label>수정용 비밀번호</label>
        <input v-model="password" type="password" placeholder="게시글 수정·삭제 시 사용됩니다 (평문 저장)" />
        <span class="hint">⚠ 교육 목적 설계로 비밀번호는 암호화 없이 저장됩니다.</span>
      </div>
      <div class="form-actions">
        <router-link class="btn btn-outline" to="/board">취소</router-link>
        <button class="btn btn-primary" @click="submitPost">{{ isEdit ? '수정 완료' : '등록' }}</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { posts as initialPosts } from '../data/mockData'

const props = defineProps({ id: { type: [String, Number], required: false } })
const route = useRoute()
const router = useRouter()
const posts = ref([...initialPosts])
const title = ref('')
const body = ref('')
const password = ref('')
const isEdit = computed(() => Boolean(props.id || route.params.id))

if (isEdit.value) {
  const target = posts.value.find((item) => String(item.id) === String(props.id || route.params.id))
  if (target) {
    title.value = target.title
    body.value = target.body
    password.value = target.password
  }
}

function submitPost() {
  if (!title.value.trim() || !body.value.trim() || !password.value) {
    alert('제목, 내용, 비밀번호를 모두 입력해주세요.')
    return
  }

  const targetId = Number(props.id || route.params.id)
  if (isEdit.value && targetId) {
    posts.value = posts.value.map((item) => (item.id === targetId ? { ...item, title: title.value, body: body.value, password: password.value } : item))
    router.push(`/board/${targetId}`)
    return
  }

  const today = new Date().toISOString().slice(0, 10)
  posts.value = [{ id: Date.now(), title: title.value, body: body.value, password: password.value, views: 0, date: today }, ...posts.value]
  router.push('/board')
}
</script>
