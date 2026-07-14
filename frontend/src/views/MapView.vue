<template>
  <section class="view-shell wide-view">
    <div class="section-head" style="margin-top: 28px;">
      <h2>부산 지역 지도</h2>
    </div>
    <div class="map-toolbar">
      <button v-for="cat in mapCategories" :key="cat" class="chip" :class="{ active: cat === activeCat }" @click="activeCat = cat">{{ cat }}</button>
    </div>
    <div id="leaflet-map"></div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { places, mapCategories } from '../data/mockData'

const route = useRoute()
const activeCat = ref('전체')
let map = null

function initMap() {
  const L = window.L
  if (!L || !document.getElementById('leaflet-map')) return
  if (!map) {
    map = L.map('leaflet-map').setView([35.13, 129.1], 11)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap contributors' }).addTo(map)
  }
  renderMarkers()
}

function renderMarkers() {
  if (!map) return
  map.eachLayer((layer) => {
    if (layer instanceof window.L.Marker) {
      map.removeLayer(layer)
    }
  })
  const filtered = places.filter((place) => activeCat.value === '전체' || place.cat === activeCat.value)
  filtered.forEach((place) => {
    const icon = window.L.divIcon({ className: '', html: `<div style="width:16px;height:16px;border-radius:50%;background:${place.cat === '관광지' ? '#1E4FD1' : place.cat === '맛집' ? '#3B6FF0' : place.cat === '숙박' ? '#7C5CFC' : place.cat === '여행코스' ? '#12A66A' : '#E8B23D'};border:3px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.35);"></div>`, iconSize: [16, 16], iconAnchor: [8, 8] })
    window.L.marker([place.lat, place.lng], { icon }).addTo(map).bindPopup(`<div class="popup-tag">${place.cat}</div><div class="popup-title">${place.name}</div><div>${place.desc}</div>`)
  })
}

watch(activeCat, () => renderMarkers())
watch(() => route.query.cat, (value) => {
  if (value) activeCat.value = value
}, { immediate: true })

onMounted(() => {
  initMap()
})
</script>
