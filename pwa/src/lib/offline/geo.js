// Lightweight geodesy — browser port of backend app/services/mission/geo.py.
// Works in a local east/north tangent plane measured in FEET about the polygon
// centroid. Accurate to sub-foot over parcel-scale areas. Keeping this identical
// to the Python keeps offline (phone) and online (server) output in lock-step.

export const EARTH_RADIUS_FT = 20902231.0
export const FEET_PER_METER = 3.280839895
export const METERS_PER_FOOT = 0.3048

export function feetPerDegreeLat() {
  return (EARTH_RADIUS_FT * Math.PI) / 180.0
}

export function feetPerDegreeLng(latDeg) {
  return ((EARTH_RADIUS_FT * Math.PI) / 180.0) * Math.cos((latDeg * Math.PI) / 180.0)
}

// Area-weighted centroid of a closed ring of [lng, lat] points.
export function ringCentroid(ring) {
  const pts = ring.slice()
  if (pts[0][0] !== pts[pts.length - 1][0] || pts[0][1] !== pts[pts.length - 1][1]) {
    pts.push(pts[0])
  }
  let a = 0,
    cx = 0,
    cy = 0
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i]
    const [x1, y1] = pts[i + 1]
    const cross = x0 * y1 - x1 * y0
    a += cross
    cx += (x0 + x1) * cross
    cy += (y0 + y1) * cross
  }
  if (Math.abs(a) < 1e-12) {
    const n = pts.length - 1
    let sx = 0,
      sy = 0
    for (let i = 0; i < n; i++) {
      sx += pts[i][0]
      sy += pts[i][1]
    }
    return [sx / n, sy / n]
  }
  a *= 0.5
  return [cx / (6 * a), cy / (6 * a)]
}

export class LocalPlane {
  constructor([originLng, originLat]) {
    this.originLng = originLng
    this.originLat = originLat
    this.fpdLat = feetPerDegreeLat()
    this.fpdLng = feetPerDegreeLng(originLat)
  }
  toFeet([lng, lat]) {
    return [(lng - this.originLng) * this.fpdLng, (lat - this.originLat) * this.fpdLat]
  }
  toLngLat(east, north) {
    return [this.originLng + east / this.fpdLng, this.originLat + north / this.fpdLat]
  }
}

export function boundingBoxFt(plane, ring) {
  const pts = ring.map((c) => plane.toFeet(c))
  const es = pts.map((p) => p[0])
  const ns = pts.map((p) => p[1])
  return [Math.min(...es), Math.min(...ns), Math.max(...es), Math.max(...ns)]
}

// Ray-casting point-in-polygon test in degrees (lng/lat) — used for parcel
// containment against cached county GeoJSON.
export function pointInRing(lng, lat, ring) {
  let inside = false
  const n = ring.length
  let j = n - 1
  for (let i = 0; i < n; i++) {
    const xi = ring[i][0],
      yi = ring[i][1]
    const xj = ring[j][0],
      yj = ring[j][1]
    if (yi > lat !== yj > lat && lng < ((xj - xi) * (lat - yi)) / (yj - yi + 1e-15) + xi) {
      inside = !inside
    }
    j = i
  }
  return inside
}

export function polygonDimensionsFt(plane, ring) {
  const [minE, minN, maxE, maxN] = boundingBoxFt(plane, ring)
  return [maxE - minE, maxN - minN]
}

// Shoelace area in square feet (for the "measuring" readout).
export function polygonAreaSqft(ring) {
  const plane = new LocalPlane(ringCentroid(ring))
  const pts = ring.map((c) => plane.toFeet(c))
  let area = 0
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i]
    const [x1, y1] = pts[i + 1]
    area += x0 * y1 - x1 * y0
  }
  // close the ring if needed
  const [xl, yl] = pts[pts.length - 1]
  const [xf, yf] = pts[0]
  area += xl * yf - xf * yl
  return Math.abs(area) / 2.0
}

// Extract the outer ring from a GeoJSON Polygon / MultiPolygon / Feature.
export function outerRing(geojson) {
  let geom = geojson
  if (geom.type === 'Feature') geom = geom.geometry
  if (geom.type === 'FeatureCollection') geom = geom.features[0].geometry
  if (geom.type === 'Polygon') return geom.coordinates[0].map(([x, y]) => [+x, +y])
  if (geom.type === 'MultiPolygon') return geom.coordinates[0][0].map(([x, y]) => [+x, +y])
  throw new Error(`Unsupported geometry type: ${geom.type}`)
}
