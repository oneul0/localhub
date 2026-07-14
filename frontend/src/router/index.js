import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlacesView from '../views/PlacesView.vue'
import BoardView from '../views/BoardView.vue'
import ChatbotView from '../views/ChatbotView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/places', name: 'places', component: PlacesView },
  { path: '/board', name: 'board', component: BoardView },
  { path: '/chatbot', name: 'chatbot', component: ChatbotView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
