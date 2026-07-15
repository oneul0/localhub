import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BoardView from '../views/BoardView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import PostFormView from '../views/PostFormView.vue'
import MapView from '../views/MapView.vue'
import FestivalCalendarView from '../views/FestivalCalendarView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/board', name: 'board', component: BoardView },
  { path: '/board/:id', name: 'post-detail', component: PostDetailView, props: true },
  { path: '/write', name: 'post-create', component: PostFormView },
  { path: '/board/:id/edit', name: 'post-edit', component: PostFormView, props: true },
  { path: '/map', name: 'map', component: MapView },
  { path: '/festivals', name: 'festivals', component: FestivalCalendarView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
