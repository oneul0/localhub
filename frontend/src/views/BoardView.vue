<template>
  <section class="view-shell wide-view">
    <div class="section-head" style="margin-top: 28px;">
      <h2>부산 지역 게시판</h2>
      <router-link class="btn btn-primary btn-sm" to="/write">+ 글쓰기</router-link>
    </div>

    <div class="toolbar">
      <div class="search-wrap">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="11" cy="11" r="7" stroke="#16232A" stroke-width="2" /><path d="M21 21l-4-4" stroke="#16232A" stroke-width="2" stroke-linecap="round" /></svg>
        <input v-model="query" type="text" placeholder="제목, 내용, 키워드로 검색 (예: 야경, 밀면)" />
      </div>
      <select v-model="sort">
        <option value="latest">최신순</option>
        <option value="views">조회수순</option>
      </select>
    </div>

    <div class="col-head">
      <span>제목</span><span style="text-align:right;">조회수</span><span style="text-align:right;">작성일</span>
    </div>
    <div class="board-box">
      <div v-if="pagedPosts.length" v-for="post in pagedPosts" :key="post.post_id" class="post-row" @click="openDetail(post.post_id)">
        <span class="post-title">{{ post.title }}</span>
        <span class="post-views">👁 {{ post.view_count }}</span>
        <span class="post-date mono">{{ formatDate(post.created_at) }}</span>
      </div>
      <div v-else class="empty-state">검색 결과가 없어요. 다른 키워드로 시도해보세요.</div>
    </div>

    <div class="pagination">
      <button v-for="page in totalPages" :key="page" :class="{ active: page === currentPage }" @click="currentPage = page">{{ page }}</button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPosts } from '../api/posts'

const router = useRouter()
const posts = ref([])
const query = ref('')
const sort = ref('latest')
const currentPage = ref(1)
const pageSize = 4

const filteredPosts = computed(() => {
  const q = query.value.trim().toLowerCase()
  const base = [...posts.value].filter((post) => !q || post.title.toLowerCase().includes(q) || post.content.toLowerCase().includes(q))
  return base.sort((a, b) => (sort.value === 'views' ? b.view_count - a.view_count : b.post_id - a.post_id))
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPosts.value.length / pageSize)))
const pagedPosts = computed(() => filteredPosts.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

async function loadPosts() {
  try {
    const data = await getPosts(1, 100)
    posts.value = data
  } catch (error) {
    console.error('게시글 로딩 실패:', error)
    alert('게시글을 불러오지 못했습니다.')
  }
}

function formatDate(value) {
  return value ? value.slice(0, 10) : ''
}

function openDetail(id) {
  router.push(`/board/${id}`)
}

onMounted(() => {
  loadPosts()
})
</script>
