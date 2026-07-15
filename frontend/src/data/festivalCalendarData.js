import festivalData from '../../../data/부산_축제_2026.json'
import { places } from './busanMapData'

const RECOMMENDATION_CATEGORIES = ['관광지', '숙박', '여행코스']

export const festivalSource = Object.freeze({
  name: festivalData.sourceName,
  url: festivalData.sourceUrl,
  updatedAt: festivalData.updatedAt,
})

export const festivals = Object.freeze(
  festivalData.items.map((item) => ({
    ...item,
    lat: Number(item.mapy),
    lng: Number(item.mapx),
  })),
)

function distanceInKilometers(from, to) {
  const toRadians = (degrees) => (degrees * Math.PI) / 180
  const earthRadius = 6371
  const latitudeDelta = toRadians(to.lat - from.lat)
  const longitudeDelta = toRadians(to.lng - from.lng)
  const fromLatitude = toRadians(from.lat)
  const toLatitude = toRadians(to.lat)

  const value =
    Math.sin(latitudeDelta / 2) ** 2 +
    Math.cos(fromLatitude) *
      Math.cos(toLatitude) *
      Math.sin(longitudeDelta / 2) ** 2

  return earthRadius * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value))
}

export function nearbyFestivalPlaces(festival) {
  if (!festival) return []

  return RECOMMENDATION_CATEGORIES.map((category) => {
    const nearest = places
      .filter((place) => place.category === category)
      .map((place) => ({
        ...place,
        distance: distanceInKilometers(festival, place),
      }))
      .sort((a, b) => a.distance - b.distance)[0]

    return nearest
  }).filter(Boolean)
}
