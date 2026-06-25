// Client-side mission generation — assembles a DJI mapping .kmz entirely in the
// browser so the field workflow works with no connectivity (spec §10.1).
// Browser port of app/services/mission/kmz_builder.py using JSZip.
import JSZip from 'jszip'
import { outerRing } from './geo'
import { planGrid } from './grid'
import { buildTemplateKml, buildWaylinesWpml, DRONE_ENUM } from './wpml'
import { computePrintScale } from './scale'

export function validateParams({ altitudeFt = 120, drone = 'mini4pro' } = {}) {
  if (!(altitudeFt >= 80 && altitudeFt <= 200)) {
    throw new Error('Altitude must be between 80 and 200 ft (spec §6.1).')
  }
  if (!(drone in DRONE_ENUM)) throw new Error(`Unknown drone '${drone}'.`)
}

// Returns { kmzBlob, summary, plan, scale, templateKml, waylinesWpml }.
export async function buildMissionKmz(parcelGeojson, params = {}) {
  validateParams(params)
  const droneEnum = DRONE_ENUM[params.drone ?? 'mini4pro']
  const ring = outerRing(parcelGeojson)

  const plan = planGrid(parcelGeojson, {
    altitudeFt: params.altitudeFt ?? 120,
    forwardOverlap: params.forwardOverlap ?? 0.8,
    sideOverlap: params.sideOverlap ?? 0.75,
    bufferFt: params.bufferFt ?? 15
  })

  const templateKml = buildTemplateKml(ring, { droneEnum, finishAction: params.finishAction ?? 'goHome' })
  const waylinesWpml = buildWaylinesWpml(plan, {
    droneEnum,
    finishAction: params.finishAction ?? 'goHome',
    autoFlightSpeedMps: params.autoFlightSpeedMps ?? 6
  })

  const zip = new JSZip()
  const wpmz = zip.folder('wpmz')
  wpmz.file('template.kml', templateKml)
  wpmz.file('waylines.wpml', waylinesWpml)
  const kmzBlob = await zip.generateAsync({
    type: 'blob',
    mimeType: 'application/vnd.google-earth.kmz',
    compression: 'DEFLATE'
  })

  const scale = computePrintScale(parcelGeojson)
  const summary = {
    waypoints: plan.waypoints.length,
    line_count: plan.lineCount,
    line_spacing_ft: plan.lineSpacingFt,
    photo_spacing_ft: plan.photoSpacingFt,
    flight_axis: plan.flightAxis,
    altitude_ft: plan.altitudeFt,
    estimated_photos: plan.estimatedPhotos,
    kmz_size_bytes: kmzBlob.size
  }

  return { kmzBlob, summary, plan, scale, templateKml, waylinesWpml }
}
