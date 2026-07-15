import { createApp } from 'vue'
import { createPinia } from 'pinia'
import L from 'leaflet'

import App from './App.vue'
import router from './router'

import './style.css'
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// Leaflet이 기본 상대경로로 이미지를 찾지 않도록 제거
delete L.Icon.Default.prototype._getIconUrl

// Vite가 빌드한 실제 이미지 경로 사용
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.mount('#app')