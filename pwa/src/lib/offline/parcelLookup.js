// Offline parcel lookup — find the parcel containing a point by testing it
// against the cached county GeoJSON in IndexedDB (spec §10.1). This is the
// browser equivalent of the backend PostGIS ST_Contains query (spec §5.3), so
// the field flow needs no server.
import { pointInRing } from './geo'
import { getCountyBundle, getCachedCounties } from '../../db/parcelCache'

function ringsOf(geometry) {
  // Yields outer rings to test for containment.
  if (geometry.type === 'Polygon') return [geometry.coordinates[0]]
  if (geometry.type === 'MultiPolygon') return geometry.coordinates.map((poly) => poly[0])
  return []
}

// Search one county's cached bundle. Returns a parcel-shaped object or null.
export function findParcelInBundle(bundle, lng, lat, county) {
  if (!bundle?.geojson?.features) return null
  for (const feature of bundle.geojson.features) {
    const geom = feature.geometry
    if (!geom) continue
    for (const ring of ringsOf(geom)) {
      if (pointInRing(lng, lat, ring.map(([x, y]) => [+x, +y]))) {
        const props = feature.properties || {}
        return {
          parcel_id: props.parcel_id || props.PARCELID || props.PIN || feature.id || null,
          owner: props.owner || props.OWNER || null,
          address: props.address || props.ADDRESS || props.SITEADDR || null,
          county,
          geojson: { type: 'Feature', geometry: geom, properties: props }
        }
      }
    }
  }
  return null
}

// Look up a point across cached counties (optionally a single hinted county).
export async function lookupParcelOffline(lng, lat, countyHint = null) {
  let counties
  if (countyHint) {
    counties = [countyHint]
  } else {
    counties = (await getCachedCounties()).map((c) => c.county)
  }
  for (const county of counties) {
    const bundle = await getCountyBundle(county)
    const parcel = findParcelInBundle(bundle, lng, lat, county)
    if (parcel) return parcel
  }
  return null
}
