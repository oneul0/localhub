<template>
  <section class="view-shell">
    <div class="hero">
      <div class="hero-eyebrow">공공데이터 기반 · 익명 커뮤니티</div>
      <h1>부산, 오늘은<br />어디부터 걸어볼까요?</h1>
      <p>바다와 골목이 함께 있는 도시, 부산의 관광지·맛집·축제 정보를 한곳에서 모아보고, 주민들과 실시간으로 이야기를 나눠보세요.</p>
      <div class="hero-actions">
        <router-link class="btn btn-primary" to="/board">게시판 둘러보기 →</router-link>
        <router-link class="btn btn-ghost" to="/map">지도로 보기</router-link>
      </div>
    </div>
    <svg class="wave" viewBox="0 0 1200 60" preserveAspectRatio="none"><path d="M0,30 C150,60 350,0 600,30 C850,60 1050,0 1200,30 L1200,60 L0,60 Z" fill="var(--paper)" /></svg>

    <SectionHeader title="카테고리 바로가기" />
    <div class="cat-grid">
      <CategoryCard to="/map?cat=관광지" icon="🏞️" icon-bg="#E5EBFB" title="관광지" description="해운대, 태종대, 감천문화마을 등 부산의 명소를 지도에서 바로 확인해요." />
      <CategoryCard to="/map?cat=숙박" icon="🏨" icon-bg="#EFEAFE" title="숙박" description="해운대·기장·원도심 권역의 호텔과 게스트하우스 위치를 살펴봐요." />
      <CategoryCard to="/map?cat=여행코스" icon="🧭" icon-bg="#E4F7EE" title="여행코스" description="도보·드라이브로 즐기는 부산 추천 여행 코스를 지도에서 만나요." />
    </div>

    <SectionHeader title="최근 게시글" to="/board" link-text="전체보기 →" />
    <PostList :posts="recentPosts" @select="goDetail" />

    <SectionHeader title="지도 미리보기" to="/map" link-text="전체 지도 보기 →" />
    <div id="leaflet-map-home"></div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { places } from '../data/mockData'
import SectionHeader from '../components/shared/SectionHeader.vue'
import CategoryCard from '../components/shared/CategoryCard.vue'
import PostList from '../components/shared/PostList.vue'
import { getPosts } from '../api/posts'

const router = useRouter()
const recentPosts = ref([])

async function loadRecentPosts() {
  try {
    const posts = await getPosts(1, 4)
    recentPosts.value = posts.map((post) => ({
      id: post.post_id,
      title: post.title,
      views: post.view_count,
      date: post.created_at.slice(0, 10),
      body: post.content,
      password: ''
    }))
  } catch (error) {
    console.error('최근 게시글 로딩 실패:', error)
  }
}

function goDetail(id) {
  router.push(`/board/${id}`)
}

onMounted(() => {
  loadRecentPosts()

  const L = window.L
  if (!L || document.getElementById('leaflet-map-home')._leaflet_id) return
  const map = L.map('leaflet-map-home', { scrollWheelZoom: false }).setView([35.13, 129.1], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map)
  places.forEach((place) => {
    L.marker([place.lat, place.lng]).addTo(map).bindPopup(`<div class="popup-tag">${place.cat}</div><div class="popup-title">${place.name}</div><div>${place.desc}</div>`)
  })
})
</script>
