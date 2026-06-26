import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

// MapLibre GL preview of a parcel boundary (spec §3.1, §3.3 Parcel Preview).
// Uses an offline-capable vector style; the boundary is drawn as a fill+line.
export default function ParcelMap({ geojson, center, height = 300, markers = [], onPick }) {
  const ref = useRef(null)
  const mapRef = useRef(null)
  const markerObjs = useRef([])
  // Keep the latest onPick so the (once-registered) click handler never calls a
  // stale closure — otherwise the marker-type selector would be ignored.
  const onPickRef = useRef(onPick)
  onPickRef.current = onPick

  useEffect(() => {
    if (!ref.current) return
    const styleUrl =
      import.meta.env.VITE_MAP_STYLE_URL || 'https://demotiles.maplibre.org/style.json'
    const map = new maplibregl.Map({
      container: ref.current,
      style: styleUrl,
      center: center || [-83.97, 35.75],
      zoom: 16
    })
    mapRef.current = map

    map.on('load', () => {
      if (!geojson) return
      map.addSource('parcel', { type: 'geojson', data: geojson })
      map.addLayer({
        id: 'parcel-fill',
        type: 'fill',
        source: 'parcel',
        paint: { 'fill-color': '#7BAFD4', 'fill-opacity': 0.25 }
      })
      map.addLayer({
        id: 'parcel-line',
        type: 'line',
        source: 'parcel',
        paint: { 'line-color': '#1B3A5C', 'line-width': 3 }
      })
      try {
        const b = new maplibregl.LngLatBounds()
        const ring = geojson.geometry?.coordinates?.[0] || geojson.coordinates?.[0] || []
        ring.forEach((c) => b.extend(c))
        if (!b.isEmpty()) map.fitBounds(b, { padding: 40, duration: 0 })
      } catch {
        /* ignore fit errors */
      }
    })

    // Tap-to-add support for the annotation layer (spec §12). The handler reads
    // the current onPick via a ref so the live marker-type selection is used.
    if (onPickRef.current) {
      map.on('click', (e) => onPickRef.current?.([e.lngLat.lng, e.lngLat.lat]))
      map.getCanvas().style.cursor = 'crosshair'
    }

    return () => map.remove()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [geojson])

  // Render annotation markers without recreating the map.
  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    markerObjs.current.forEach((m) => m.remove())
    markerObjs.current = (markers || []).map(({ lng, lat, label }) => {
      const el = document.createElement('div')
      el.title = label || ''
      el.style.cssText =
        'width:14px;height:14px;border-radius:50%;background:#1B3A5C;border:2px solid #fff;box-shadow:0 0 0 1px #1B3A5C'
      return new maplibregl.Marker({ element: el }).setLngLat([lng, lat]).addTo(map)
    })
  }, [markers])

  return <div ref={ref} style={{ height }} className="w-full rounded-xl overflow-hidden" />
}
