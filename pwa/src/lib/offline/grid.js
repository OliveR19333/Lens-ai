// Lawnmower grid planner — browser port of app/services/mission/grid.py.
import { LocalPlane, boundingBoxFt, ringCentroid, outerRing } from './geo'

// DJI Mini 4 Pro wide camera defaults (1/1.3" sensor, ~24mm equiv).
export const DEFAULT_CAMERA = {
  name: 'DJI Mini 4 Pro',
  sensorWidthMm: 9.6,
  sensorHeightMm: 7.2,
  focalLengthMm: 6.72
}

export function footprintFt(camera, altitudeFt) {
  const across = (altitudeFt * camera.sensorWidthMm) / camera.focalLengthMm
  const along = (altitudeFt * camera.sensorHeightMm) / camera.focalLengthMm
  return [across, along]
}

// Returns { waypoints:[{lng,lat,altitudeFt}], lineSpacingFt, photoSpacingFt,
//           lineCount, altitudeFt, flightAxis, estimatedPhotos }
export function planGrid(parcelGeojson, opts = {}) {
  const altitudeFt = opts.altitudeFt ?? 120
  const forwardOverlap = opts.forwardOverlap ?? 0.8
  const sideOverlap = opts.sideOverlap ?? 0.75
  const bufferFt = opts.bufferFt ?? 15
  const camera = opts.camera ?? DEFAULT_CAMERA

  if (!(forwardOverlap >= 0 && forwardOverlap < 1) || !(sideOverlap >= 0 && sideOverlap < 1)) {
    throw new Error('Overlaps must be in [0, 1).')
  }
  if (altitudeFt <= 0) throw new Error('Altitude must be positive.')

  const ring = outerRing(parcelGeojson)
  const plane = new LocalPlane(ringCentroid(ring))
  let [minE, minN, maxE, maxN] = boundingBoxFt(plane, ring)
  minE -= bufferFt
  minN -= bufferFt
  maxE += bufferFt
  maxN += bufferFt

  const width = maxE - minE
  const height = maxN - minN
  const [acrossFt] = footprintFt(camera, altitudeFt)
  const [, alongFt] = footprintFt(camera, altitudeFt)
  const lineSpacing = Math.max(acrossFt * (1 - sideOverlap), 1)
  const photoSpacing = Math.max(alongFt * (1 - forwardOverlap), 1)

  const linesAlongNorth = height >= width
  const flightAxis = linesAlongNorth ? 'north-south' : 'east-west'

  const waypoints = []
  let nLines
  if (linesAlongNorth) {
    nLines = Math.max(Math.ceil(width / lineSpacing) + 1, 1)
    for (let i = 0; i < nLines; i++) {
      const e = Math.min(minE + i * lineSpacing, maxE)
      const nPhotos = Math.max(Math.ceil(height / photoSpacing) + 1, 2)
      let coords = []
      for (let j = 0; j < nPhotos; j++) coords.push(Math.min(minN + j * photoSpacing, maxN))
      if (i % 2 === 1) coords.reverse()
      for (const north of coords) {
        const [lng, lat] = plane.toLngLat(e, north)
        waypoints.push({ lng, lat, altitudeFt })
      }
    }
  } else {
    nLines = Math.max(Math.ceil(height / lineSpacing) + 1, 1)
    for (let i = 0; i < nLines; i++) {
      const north = Math.min(minN + i * lineSpacing, maxN)
      const nPhotos = Math.max(Math.ceil(width / photoSpacing) + 1, 2)
      let coords = []
      for (let j = 0; j < nPhotos; j++) coords.push(Math.min(minE + j * photoSpacing, maxE))
      if (i % 2 === 1) coords.reverse()
      for (const east of coords) {
        const [lng, lat] = plane.toLngLat(east, north)
        waypoints.push({ lng, lat, altitudeFt })
      }
    }
  }

  return {
    waypoints,
    lineSpacingFt: Math.round(lineSpacing * 100) / 100,
    photoSpacingFt: Math.round(photoSpacing * 100) / 100,
    lineCount: nLines,
    altitudeFt,
    flightAxis,
    estimatedPhotos: waypoints.length
  }
}
