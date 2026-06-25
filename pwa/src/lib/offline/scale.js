// Best-fit print-scale + measuring — browser port of app/services/maps/scale.py.
import { LocalPlane, ringCentroid, polygonDimensionsFt, polygonAreaSqft, outerRing } from './geo'

export const PRINTABLE_WIDTH_IN = 7.5
export const PRINTABLE_HEIGHT_IN = 10.0
export const TARGET_GRID_WIDTH_IN = 25.0
export const TARGET_GRID_HEIGHT_IN = 30.0
export const PAPER_WIDTH_IN = 8.5

export function computePrintScale(parcelGeojson, roundToFt = 5) {
  const ring = outerRing(parcelGeojson)
  const plane = new LocalPlane(ringCentroid(ring))
  const [widthFt, heightFt] = polygonDimensionsFt(plane, ring)

  const raw = Math.max(widthFt / PRINTABLE_WIDTH_IN, heightFt / PRINTABLE_HEIGHT_IN)
  const feetPerInch = raw > 0 ? Math.ceil(raw / roundToFt) * roundToFt : roundToFt
  const enlargement = TARGET_GRID_WIDTH_IN / PAPER_WIDTH_IN
  const label = `1 inch = ${feetPerInch} feet`
  const note = `Scale: ${label} | Enlarge ${enlargement.toFixed(2)}x for ${Math.round(
    TARGET_GRID_WIDTH_IN
  )}x${Math.round(TARGET_GRID_HEIGHT_IN)} grid`

  return {
    feetPerInch,
    parcelWidthFt: Math.round(widthFt * 10) / 10,
    parcelHeightFt: Math.round(heightFt * 10) / 10,
    parcelAreaSqft: Math.round(polygonAreaSqft(ring)),
    parcelAreaAcres: Math.round((polygonAreaSqft(ring) / 43560) * 100) / 100,
    enlargementFactor: Math.round(enlargement * 100) / 100,
    label,
    note
  }
}
