<template>
  <section class="view-shell festival-view">
    <div class="festival-hero">
      <div>
        <p class="festival-eyebrow">BUSAN FESTIVAL CALENDAR</p>
        <h1>부산 축제 캘린더</h1>
        <p class="festival-intro">
          공식 축제 일정과 관광지·숙박·여행코스 데이터를 한 번에 확인하세요.
        </p>
      </div>
      <a
        class="source-link"
        :href="festivalSource.url"
        target="_blank"
        rel="noopener noreferrer"
      >
        {{ festivalSource.name }}에서 확인 ↗
      </a>
    </div>

    <div class="calendar-layout">
      <div class="calendar-card">
        <div class="calendar-toolbar">
          <div class="month-navigation">
            <button type="button" aria-label="이전 달" @click="moveMonth(-1)">‹</button>
            <h2>{{ monthLabel }}</h2>
            <button type="button" aria-label="다음 달" @click="moveMonth(1)">›</button>
          </div>
          <div class="calendar-summary">
            <span>{{ monthFestivalCount }}개 일정</span>
            <button type="button" class="today-button" @click="goToday">오늘</button>
          </div>
        </div>

        <div class="weekday-row" aria-hidden="true">
          <span v-for="weekday in weekdays" :key="weekday">{{ weekday }}</span>
        </div>

        <div class="calendar-grid">
          <button
            v-for="day in calendarDays"
            :key="day.key"
            type="button"
            class="calendar-day"
            :class="{
              muted: !day.isCurrentMonth,
              today: day.key === todayKey,
              selected: day.key === selectedDate,
              'has-events': day.events.length,
            }"
            :aria-label="`${day.key}, 축제 ${day.events.length}개`"
            @click="selectDay(day)"
          >
            <span class="day-number">{{ day.date.getDate() }}</span>
            <span class="day-events">
              <span
                v-for="festival in day.events.slice(0, 2)"
                :key="festival.id"
                class="event-chip"
                :class="categoryClass(festival.category)"
                @click.stop="selectFestival(day, festival)"
              >
                {{ festival.title }}
              </span>
              <span v-if="day.events.length > 2" class="more-events">
                +{{ day.events.length - 2 }}개
              </span>
            </span>
          </button>
        </div>
      </div>

      <aside class="schedule-panel">
        <div class="schedule-heading">
          <div>
            <p>선택한 날짜</p>
            <h2>{{ selectedDateLabel }}</h2>
          </div>
          <span>{{ selectedFestivals.length }}개</span>
        </div>

        <div v-if="selectedFestivals.length" class="schedule-list">
          <button
            v-for="festival in selectedFestivals"
            :key="festival.id"
            type="button"
            class="schedule-item"
            :class="{ active: festival.id === activeFestival?.id }"
            @click="activeFestivalId = festival.id"
          >
            <span class="schedule-accent" :class="categoryClass(festival.category)" />
            <span>
              <span class="schedule-category">{{ festival.category }}</span>
              <strong>{{ festival.title }}</strong>
              <small>{{ formatPeriod(festival) }} · {{ festival.venue }}</small>
            </span>
          </button>
        </div>

        <div v-else class="schedule-empty">
          <span>📅</span>
          <strong>등록된 축제가 없습니다</strong>
          <p>일정이 표시된 날짜를 선택해 보세요.</p>
        </div>

        <div v-if="activeFestival" class="festival-detail">
          <div class="detail-topline">
            <span class="status-badge" :class="festivalStatus(activeFestival).className">
              {{ festivalStatus(activeFestival).label }}
            </span>
            <span>{{ activeFestival.district }}</span>
          </div>
          <h3>{{ activeFestival.title }}</h3>
          <p>{{ activeFestival.summary }}</p>
          <dl>
            <div>
              <dt>기간</dt>
              <dd>{{ formatPeriod(activeFestival) }}</dd>
            </div>
            <div>
              <dt>장소</dt>
              <dd>{{ activeFestival.venue }}</dd>
            </div>
          </dl>
          <a
            :href="activeFestival.sourceUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="official-link"
          >
            공식 일정 보기 ↗
          </a>
        </div>
      </aside>
    </div>

    <section v-if="activeFestival" class="nearby-section">
      <div class="nearby-heading">
        <div>
          <p>LOCAL DATA RECOMMENDATION</p>
          <h2>{{ activeFestival.venue }} 주변 함께 둘러보기</h2>
        </div>
        <span>관광지·숙박·여행코스 좌표 기준</span>
      </div>

      <div class="nearby-grid">
        <router-link
          v-for="place in nearbyPlaces"
          :key="place.id"
          class="nearby-card"
          :to="{
            path: '/map',
            query: { cat: place.category, district: place.district },
          }"
        >
          <div class="nearby-image" :style="imageStyle(place.image)">
            <span v-if="!place.image">{{ categoryEmoji(place.category) }}</span>
          </div>
          <div class="nearby-content">
            <span>{{ place.category }} · 약 {{ formatDistance(place.distance) }}</span>
            <h3>{{ place.name }}</h3>
            <p>{{ place.address || place.district }}</p>
          </div>
        </router-link>
      </div>
    </section>

    <p class="calendar-note">
      일정은 {{ festivalSource.updatedAt }} 기준이며 변경될 수 있습니다. 방문 전 공식 페이지를 확인하세요.
    </p>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  festivalSource,
  festivals,
  nearbyFestivalPlaces,
} from '../data/festivalCalendarData'

const weekdays = ['일', '월', '화', '수', '목', '금', '토']
const today = new Date()
const visibleMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const selectedDate = ref(toDateKey(today))
const activeFestivalId = ref(null)

const monthLabel = computed(() =>
  new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
  }).format(visibleMonth.value),
)

const todayKey = toDateKey(today)

const calendarDays = computed(() => {
  const year = visibleMonth.value.getFullYear()
  const month = visibleMonth.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const gridStart = new Date(year, month, 1 - firstDay.getDay())

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(
      gridStart.getFullYear(),
      gridStart.getMonth(),
      gridStart.getDate() + index,
    )
    const key = toDateKey(date)

    return {
      date,
      key,
      isCurrentMonth: date.getMonth() === month,
      events: festivalsForDate(key),
    }
  })
})

const selectedFestivals = computed(() => festivalsForDate(selectedDate.value))

const activeFestival = computed(() => {
  return (
    selectedFestivals.value.find(
      (festival) => festival.id === activeFestivalId.value,
    ) ?? selectedFestivals.value[0] ?? null
  )
})

const nearbyPlaces = computed(() => nearbyFestivalPlaces(activeFestival.value))

const selectedDateLabel = computed(() => {
  return new Intl.DateTimeFormat('ko-KR', {
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(fromDateKey(selectedDate.value))
})

const monthFestivalCount = computed(() => {
  const year = visibleMonth.value.getFullYear()
  const month = visibleMonth.value.getMonth()
  const monthStart = toDateKey(new Date(year, month, 1))
  const monthEnd = toDateKey(new Date(year, month + 1, 0))

  return festivals.filter(
    (festival) =>
      festival.startDate <= monthEnd && festival.endDate >= monthStart,
  ).length
})

function toDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function fromDateKey(value) {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function festivalsForDate(dateKey) {
  return festivals.filter(
    (festival) =>
      festival.startDate <= dateKey && festival.endDate >= dateKey,
  )
}

function moveMonth(offset) {
  const nextMonth = new Date(
    visibleMonth.value.getFullYear(),
    visibleMonth.value.getMonth() + offset,
    1,
  )
  visibleMonth.value = nextMonth
  selectedDate.value = toDateKey(nextMonth)
  activeFestivalId.value = null
}

function goToday() {
  visibleMonth.value = new Date(today.getFullYear(), today.getMonth(), 1)
  selectedDate.value = todayKey
  activeFestivalId.value = null
}

function selectDay(day) {
  selectedDate.value = day.key
  activeFestivalId.value = day.events[0]?.id ?? null

  if (!day.isCurrentMonth) {
    visibleMonth.value = new Date(
      day.date.getFullYear(),
      day.date.getMonth(),
      1,
    )
  }
}

function selectFestival(day, festival) {
  selectDay(day)
  activeFestivalId.value = festival.id
}

function formatPeriod(festival) {
  const formatter = new Intl.DateTimeFormat('ko-KR', {
    month: 'short',
    day: 'numeric',
  })
  const start = formatter.format(fromDateKey(festival.startDate))
  const end = formatter.format(fromDateKey(festival.endDate))
  return festival.startDate === festival.endDate ? start : `${start} – ${end}`
}

function festivalStatus(festival) {
  if (festival.endDate < todayKey) {
    return { label: '종료', className: 'ended' }
  }
  if (festival.startDate > todayKey) {
    return { label: '예정', className: 'upcoming' }
  }
  return { label: '진행 중', className: 'ongoing' }
}

function categoryClass(category) {
  return {
    대표축제: 'category-main',
    야간축제: 'category-night',
    '문화·전시': 'category-culture',
    체험: 'category-experience',
  }[category]
}

function categoryEmoji(category) {
  return { 관광지: '📍', 숙박: '🛏️', 여행코스: '🧭' }[category] ?? '부산'
}

function formatDistance(distance) {
  return distance < 1 ? `${Math.round(distance * 1000)}m` : `${distance.toFixed(1)}km`
}

function imageStyle(image) {
  return image
    ? { backgroundImage: `linear-gradient(180deg, transparent, rgba(16,36,92,.2)), url("${image}")` }
    : {}
}
</script>

<style scoped>
.festival-view{padding:28px 16px 0}.festival-hero{display:flex;align-items:flex-end;justify-content:space-between;gap:24px;padding:34px 38px;border-radius:22px;background:linear-gradient(125deg,#10245c,#1e4fd1 68%,#3f7fef);color:#fff;box-shadow:0 16px 42px rgba(30,79,209,.2)}.festival-eyebrow,.nearby-heading p{margin:0 0 8px;color:#e8b23d;font-size:.75rem;font-weight:800;letter-spacing:.15em}.festival-hero h1{margin:0;font-size:clamp(2rem,4vw,3rem)}.festival-intro{margin:12px 0 0;color:rgba(255,255,255,.82)}.source-link{flex:none;padding:10px 14px;border:1px solid rgba(255,255,255,.42);border-radius:10px;font-size:.82rem;font-weight:700}.calendar-layout{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:20px;margin-top:22px}.calendar-card,.schedule-panel{border:1px solid var(--line);border-radius:18px;background:#fff;box-shadow:var(--shadow)}.calendar-card{overflow:hidden}.calendar-toolbar{display:flex;align-items:center;justify-content:space-between;padding:20px 22px;border-bottom:1px solid var(--line)}.month-navigation,.calendar-summary{display:flex;align-items:center;gap:12px}.month-navigation h2{min-width:150px;margin:0;text-align:center;font-size:1.28rem}.month-navigation button,.today-button{border:1px solid var(--line);background:#fff;font-weight:800}.month-navigation button{width:36px;height:36px;border-radius:50%;font-size:1.4rem}.today-button{padding:8px 12px;border-radius:9px}.calendar-summary span{color:var(--blue);font-size:.8rem;font-weight:800}.weekday-row,.calendar-grid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr))}.weekday-row{padding:10px 0;border-bottom:1px solid var(--line);background:var(--paper-dim)}.weekday-row span{text-align:center;color:var(--ink-soft);font-size:.75rem;font-weight:800}.weekday-row span:first-child{color:#d64545}.weekday-row span:last-child{color:#1e4fd1}.calendar-day{position:relative;min-height:112px;padding:9px;border:0;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:#fff;text-align:left;transition:background .15s ease}.calendar-day:nth-child(7n){border-right:0}.calendar-day:hover{background:#f7f9fd}.calendar-day.muted{background:#fafafa;color:#a5acb0}.calendar-day.selected{background:#eef3ff;box-shadow:inset 0 0 0 2px var(--blue)}.day-number{display:inline-flex;width:27px;height:27px;align-items:center;justify-content:center;border-radius:50%;font-size:.8rem;font-weight:800}.calendar-day.today .day-number{background:var(--blue);color:#fff}.day-events{display:flex;flex-direction:column;gap:4px;margin-top:5px}.event-chip{display:block;overflow:hidden;padding:4px 6px;border-radius:5px;background:#dce7fb;color:#10245c;font-size:.67rem;font-weight:750;text-overflow:ellipsis;white-space:nowrap}.more-events{padding-left:4px;color:var(--ink-soft);font-size:.66rem;font-weight:700}.category-main{background:#ffe5da;color:#a93f1e}.category-night{background:#e8e1ff;color:#4e379b}.category-culture{background:#dce7fb;color:#173f9d}.category-experience{background:#dff5ea;color:#13724b}.schedule-panel{align-self:start;overflow:hidden}.schedule-heading{display:flex;align-items:center;justify-content:space-between;padding:21px 22px;border-bottom:1px solid var(--line)}.schedule-heading p{margin:0 0 4px;color:var(--ink-soft);font-size:.72rem;font-weight:700}.schedule-heading h2{margin:0;font-size:1.18rem}.schedule-heading>span{display:flex;width:32px;height:32px;align-items:center;justify-content:center;border-radius:50%;background:var(--paper-dim);color:var(--blue);font-size:.76rem;font-weight:800}.schedule-list{max-height:280px;overflow-y:auto}.schedule-item{display:grid;width:100%;grid-template-columns:5px 1fr;gap:12px;padding:15px 18px;border:0;border-bottom:1px solid var(--line);background:#fff;text-align:left}.schedule-item:hover,.schedule-item.active{background:#f6f8fd}.schedule-item.active{box-shadow:inset 3px 0 var(--blue)}.schedule-accent{width:5px;height:100%;min-height:50px;border-radius:8px}.schedule-item>span:last-child{display:flex;min-width:0;flex-direction:column}.schedule-category{margin-bottom:3px;color:var(--blue);font-size:.68rem;font-weight:800}.schedule-item strong{overflow:hidden;font-size:.87rem;text-overflow:ellipsis;white-space:nowrap}.schedule-item small{margin-top:5px;color:var(--ink-soft);font-size:.72rem;line-height:1.4}.schedule-empty{display:flex;min-height:230px;align-items:center;justify-content:center;flex-direction:column;padding:30px;color:var(--ink-soft);text-align:center}.schedule-empty span{font-size:2rem}.schedule-empty strong{margin-top:10px;color:var(--ink)}.schedule-empty p{margin:6px 0 0;font-size:.8rem}.festival-detail{padding:20px 22px;background:#f7f9fd}.detail-topline{display:flex;align-items:center;justify-content:space-between;color:var(--ink-soft);font-size:.72rem}.status-badge{padding:5px 9px;border-radius:100px;font-weight:800}.status-badge.ongoing{background:#daf3e6;color:#13724b}.status-badge.upcoming{background:#dce7fb;color:#173f9d}.status-badge.ended{background:#eceff2;color:#69767c}.festival-detail h3{margin:13px 0 8px;font-size:1.05rem}.festival-detail>p{margin:0;color:var(--ink-soft);font-size:.8rem;line-height:1.6}.festival-detail dl{margin:16px 0 0}.festival-detail dl div{display:grid;grid-template-columns:44px 1fr;gap:8px;margin-top:7px;font-size:.76rem}.festival-detail dt{color:var(--ink-soft);font-weight:700}.festival-detail dd{margin:0;font-weight:700}.official-link{display:inline-flex;margin-top:16px;color:var(--blue);font-size:.78rem;font-weight:800}.nearby-section{margin-top:38px}.nearby-heading{display:flex;align-items:end;justify-content:space-between;gap:16px;margin-bottom:16px}.nearby-heading p{color:var(--blue)}.nearby-heading h2{margin:0;font-size:1.4rem}.nearby-heading>span{color:var(--ink-soft);font-size:.75rem}.nearby-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.nearby-card{overflow:hidden;border:1px solid var(--line);border-radius:15px;background:#fff;box-shadow:var(--shadow);transition:transform .15s ease}.nearby-card:hover{transform:translateY(-3px)}.nearby-image{display:flex;height:145px;align-items:center;justify-content:center;background:#eaf0fb;background-position:center;background-size:cover;font-size:2rem}.nearby-content{padding:16px}.nearby-content span{color:var(--blue);font-size:.7rem;font-weight:800}.nearby-content h3{margin:6px 0;font-size:1rem}.nearby-content p{overflow:hidden;margin:0;color:var(--ink-soft);font-size:.76rem;text-overflow:ellipsis;white-space:nowrap}.calendar-note{margin:22px 0 0;color:var(--ink-soft);font-size:.73rem;text-align:right}@media(max-width:1020px){.calendar-layout{grid-template-columns:1fr}.schedule-panel{display:grid;grid-template-columns:1fr 1fr}.schedule-heading{grid-column:1/-1}.schedule-list{border-right:1px solid var(--line)}.festival-detail{min-height:100%}}@media(max-width:760px){.festival-view{padding-inline:0}.festival-hero{align-items:flex-start;flex-direction:column;padding:26px 22px}.calendar-toolbar{align-items:flex-start;flex-direction:column;gap:12px}.calendar-summary{width:100%;justify-content:space-between}.calendar-day{min-height:76px;padding:5px}.day-number{width:23px;height:23px}.event-chip{height:6px;padding:0;color:transparent}.more-events{display:none}.schedule-panel{display:block}.nearby-heading{align-items:flex-start;flex-direction:column}.nearby-grid{grid-template-columns:1fr}.calendar-note{text-align:left}}
</style>
