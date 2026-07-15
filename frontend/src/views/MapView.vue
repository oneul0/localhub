<template>
  <section class="view-shell wide-view">
    <div
      class="section-head"
      style="margin-top: 28px;"
    >
      <h2>부산 지역 지도</h2>

      <span class="see-all">
        {{ filteredPlaces.length.toLocaleString() }}개 장소
      </span>
    </div>

    <div class="toolbar">
      <div class="map-toolbar">
        <button
          v-for="cat in mapCategories"
          :key="cat"
          type="button"
          class="chip"
          :class="{ active: cat === activeCat }"
          :aria-pressed="cat === activeCat"
          @click="activeCat = cat"
        >
          {{ cat }} ({{ categoryCount(cat) }})
        </button>
      </div>

      <select
        v-model="activeDistrict"
        aria-label="부산 권역 선택"
      >
        <option
          v-for="district in mapDistricts"
          :key="district"
          :value="district"
        >
          {{ district }}
        </option>
      </select>
    </div>

    <div
      v-if="filteredPlaces.length === 0"
      class="empty-state"
    >
      선택한 조건에 해당하는 장소가 없습니다.
    </div>

    <div
      ref="mapElement"
      id="leaflet-map"
      aria-label="부산 관광 지도"
    />
  </section>
</template>

<script setup>
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet.markercluster'

import {
  CATEGORY_META,
  mapCategories,
  mapDistricts,
  places,
} from '../data/busanMapData'

const BUSAN_CENTER = [35.1796, 129.0756]

const route = useRoute()
const mapElement = ref(null)
const activeCat = ref('전체')
const activeDistrict = ref('전체 권역')

let map = null
let markerCluster = null

const filteredPlaces = computed(() => {
  return places.filter((place) => {
    const matchesCategory =
      activeCat.value === '전체' ||
      place.category === activeCat.value

    const matchesDistrict =
      activeDistrict.value === '전체 권역' ||
      place.district === activeDistrict.value

    return matchesCategory && matchesDistrict
  })
})

function categoryCount(category) {
  return places.filter((place) => {
    const matchesCategory =
      category === '전체' ||
      place.category === category

    const matchesDistrict =
      activeDistrict.value === '전체 권역' ||
      place.district === activeDistrict.value

    return matchesCategory && matchesDistrict
  }).length
}

function escapeHtml(value = '') {
  const characters = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }

  return String(value).replace(
    /[&<>"']/g,
    (character) => characters[character],
  )
}

function createMarkerIcon(category) {
  const color =
    CATEGORY_META[category]?.color ??
    '#E8B23D'

  return L.divIcon({
    className: '',
    html: `
      <div
        style="
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: ${color};
          border: 3px solid #fff;
          box-shadow: 0 2px 7px rgba(0, 0, 0, 0.38);
        "
      ></div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  })
}

function createClusterIcon(cluster) {
  const count = cluster.getChildCount()

  let background = '#1E4FD1'

  if (count >= 100) {
    background = '#10245C'
  } else if (count >= 30) {
    background = '#3B6FF0'
  }

  return L.divIcon({
    className: '',
    html: `
      <div
        style="
          display: flex;
          align-items: center;
          justify-content: center;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: 4px solid rgba(255, 255, 255, 0.9);
          background: ${background};
          color: #fff;
          font-size: 12px;
          font-weight: 800;
          box-shadow: 0 4px 14px rgba(30, 79, 209, 0.32);
        "
      >
        ${count}
      </div>
    `,
    iconSize: [42, 42],
    iconAnchor: [21, 21],
  })
}

function createPopupContent(place) {
  const categoryColor =
    CATEGORY_META[place.category]?.color ??
    '#1E4FD1'

  const address =
    place.address ||
    `부산광역시 ${place.district}`

  const imageHtml = place.image
    ? `
      <img
        src="${escapeHtml(place.image)}"
        alt=""
        loading="lazy"
        style="
          display: block;
          width: 100%;
          height: 120px;
          margin-bottom: 10px;
          border-radius: 8px;
          object-fit: cover;
        "
      >
    `
    : ''

  const telephoneHtml = place.telephone
    ? `
      <div
        style="
          margin-top: 5px;
          color: #4B5A61;
          font-size: 12px;
        "
      >
        ${escapeHtml(place.telephone)}
      </div>
    `
    : ''

  return `
    <div style="width: 240px;">
      ${imageHtml}

      <div
        class="popup-tag"
        style="color: ${categoryColor};"
      >
        ${escapeHtml(place.category)}
        ·
        ${escapeHtml(place.district)}
      </div>

      <div class="popup-title">
        ${escapeHtml(place.name)}
      </div>

      <div
        style="
          margin-top: 5px;
          color: #4B5A61;
          font-size: 12px;
          line-height: 1.5;
        "
      >
        ${escapeHtml(address)}
      </div>

      ${telephoneHtml}
    </div>
  `
}

function initMap() {
  if (!mapElement.value || map) {
    return
  }

  map = L.map(mapElement.value, {
    center: BUSAN_CENTER,
    zoom: 11,
    minZoom: 9,
    maxZoom: 18,
  })

  L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap contributors',
    },
  ).addTo(map)

  markerCluster = L.markerClusterGroup({
    showCoverageOnHover: false,
    spiderfyOnMaxZoom: true,
    zoomToBoundsOnClick: true,
    disableClusteringAtZoom: 16,
    maxClusterRadius: 48,
    iconCreateFunction: createClusterIcon,
  })

  markerCluster.addTo(map)
}

function renderMarkers() {
  if (!map || !markerCluster) {
    return
  }

  markerCluster.clearLayers()

  const markers = filteredPlaces.value.map((place) => {
    return L.marker(
      [place.lat, place.lng],
      {
        icon: createMarkerIcon(place.category),
        title: place.name,
        alt: `${place.name} ${place.category} 지도 핀`,
        riseOnHover: true,
      },
    ).bindPopup(
      createPopupContent(place),
      {
        maxWidth: 280,
        minWidth: 240,
      },
    )
  })

  markerCluster.addLayers(markers)

  if (markers.length === 0) {
    map.setView(BUSAN_CENTER, 11)
    return
  }

  if (markers.length === 1) {
    map.setView(
      markers[0].getLatLng(),
      15,
    )
    return
  }

  const bounds = markerCluster.getBounds()

  if (bounds.isValid()) {
    map.fitBounds(bounds, {
      padding: [30, 30],
      maxZoom: 14,
    })
  }
}

watch(
  [activeCat, activeDistrict],
  renderMarkers,
)

watch(
  () => route.query.cat,
  (value) => {
    if (
      typeof value === 'string' &&
      mapCategories.includes(value)
    ) {
      activeCat.value = value
    }
  },
  {
    immediate: true,
  },
)

watch(
  () => route.query.district,
  (value) => {
    if (
      typeof value === 'string' &&
      mapDistricts.includes(value)
    ) {
      activeDistrict.value = value
    }
  },
  {
    immediate: true,
  },
)

onMounted(async () => {
  await nextTick()

  initMap()
  renderMarkers()

  window.setTimeout(() => {
    map?.invalidateSize()
  }, 0)
})

onBeforeUnmount(() => {
  markerCluster?.clearLayers()
  map?.remove()

  markerCluster = null
  map = null
})
</script>