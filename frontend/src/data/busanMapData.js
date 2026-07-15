import attractionData from '../../../data/부산_관광지.json'
import accommodationData from '../../../data/부산_숙박.json'
import courseData from '../../../data/부산_여행코스.json'
import { places as mockPlaces } from './mockData'

export const CATEGORY_META = Object.freeze({
  관광지: {
    label: '관광지',
    color: '#1E4FD1',
  },
  맛집: {
    label: '맛집',
    color: '#F05A47',
  },
  숙박: {
    label: '숙박',
    color: '#7C5CFC',
  },
  여행코스: {
    label: '여행코스',
    color: '#12A66A',
  },
})

const CATEGORY_ORDER = [
  '관광지',
  '맛집',
  '숙박',
  '여행코스',
]

const DISTRICT_CODE_MAP = Object.freeze({
  110: '중구',
  140: '서구',
  170: '동구',
  200: '영도구',
  230: '부산진구',
  260: '동래구',
  290: '남구',
  320: '북구',
  350: '해운대구',
  380: '사하구',
  410: '금정구',
  440: '강서구',
  470: '연제구',
  500: '수영구',
  530: '사상구',
  710: '기장군',
})

const BUSAN_DISTRICTS = [
  '중구',
  '서구',
  '동구',
  '영도구',
  '부산진구',
  '동래구',
  '남구',
  '북구',
  '해운대구',
  '사하구',
  '금정구',
  '강서구',
  '연제구',
  '수영구',
  '사상구',
  '기장군',
]

function districtFromAddress(address = '') {
  const match = address.match(
    /(?:부산광역시|부산)\s+([^\s]+(?:구|군))/,
  )

  return match?.[1] ?? ''
}

function normalizeImageUrl(url = '') {
  return url.replace(/^http:\/\//, 'https://')
}

function hasValidBusanCoordinates(place) {
  return (
    Number.isFinite(place.lat) &&
    Number.isFinite(place.lng) &&
    place.lat >= 34.8 &&
    place.lat <= 35.5 &&
    place.lng >= 128.7 &&
    place.lng <= 129.4
  )
}

export function normalizeTourData(source, category) {
  const items = Array.isArray(source)
    ? source
    : source?.items ?? []

  return items
    .map((item) => {
      const district =
        DISTRICT_CODE_MAP[String(item.lDongSignguCd)] ||
        districtFromAddress(item.addr1)

      return {
        id: `${category}-${item.contentid}`,
        contentId: String(item.contentid ?? ''),
        category,
        name: item.title?.trim() || '이름 없는 장소',
        address: [item.addr1, item.addr2]
          .filter(Boolean)
          .join(' ')
          .trim(),
        district: district || '권역 미상',
        lat: Number(item.mapy),
        lng: Number(item.mapx),
        image: normalizeImageUrl(
          item.firstimage || item.firstimage2,
        ),
        telephone: item.tel?.trim() || '',
      }
    })
    .filter(hasValidBusanCoordinates)
}

function normalizeMockRestaurants(items) {
  return items
    .filter((item) => {
      const category = item.category ?? item.cat
      return category === '맛집'
    })
    .map((item, index) => {
      const address =
        item.address ??
        item.addr ??
        item.desc ??
        ''

      return {
        id: `맛집-${item.id ?? index}`,
        contentId: String(item.contentid ?? item.id ?? ''),
        category: '맛집',
        name: item.name ?? item.title ?? '이름 없는 맛집',
        address,
        district:
          item.district ||
          districtFromAddress(address) ||
          '권역 미상',
        lat: Number(item.lat ?? item.mapy),
        lng: Number(item.lng ?? item.mapx),
        image: normalizeImageUrl(
          item.image ??
          item.firstimage ??
          '',
        ),
        telephone: item.telephone ?? item.tel ?? '',
      }
    })
    .filter(hasValidBusanCoordinates)
}

export const places = Object.freeze([
  ...normalizeTourData(attractionData, '관광지'),
  ...normalizeMockRestaurants(mockPlaces),
  ...normalizeTourData(accommodationData, '숙박'),
  ...normalizeTourData(courseData, '여행코스'),
])

export const mapCategories = Object.freeze([
  '전체',
  ...CATEGORY_ORDER.filter((category) =>
    places.some((place) => place.category === category),
  ),
])

export const mapDistricts = Object.freeze([
  '전체 권역',
  ...BUSAN_DISTRICTS.filter((district) =>
    places.some((place) => place.district === district),
  ),
])