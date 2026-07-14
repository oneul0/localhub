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
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createPost, getPostById, updatePost } from '../api/posts'

const props = defineProps({ id: { type: [String, Number], required: false } })
const route = useRoute()
const router = useRouter()
const title = ref('')
const body = ref('')
const password = ref('')
const isEdit = computed(() => Boolean(props.id || route.params.id))

async function loadPost() {
  const targetId = props.id || route.params.id
  if (!isEdit.value || !targetId) return
  try {
    const post = await getPostById(targetId)
    title.value = post.title
    body.value = post.content
    password.value = ''
  } catch (error) {
    console.error('수정용 게시글 조회 실패:', error)
    alert('기존 게시글 정보를 불러오지 못했습니다.')
  }
}

async function submitPost() {
  if (!title.value.trim() || !body.value.trim() || !password.value) {
    alert('제목, 내용, 비밀번호를 모두 입력해주세요.')
    return
  }

  try {
    const targetId = Number(props.id || route.params.id)
    if (isEdit.value && targetId) {
      await updatePost(targetId, { title: title.value, content: body.value, password: password.value })
      router.push(`/board/${targetId}`)
      return
    }

    await createPost({ title: title.value, content: body.value, password: password.value })
    router.push('/board')
  } catch (error) {
    console.error('게시글 저장 실패:', error)
    alert('게시글 저장에 실패했습니다.')
  }
}

onMounted(() => {
  loadPost()
})
</script>
