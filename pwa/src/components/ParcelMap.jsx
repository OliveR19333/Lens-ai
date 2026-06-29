import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

// High-resolution aerial imagery basemap (Esri World Imagery — free, no API key)
// with a place-labels overlay, so you can actually see rooftops, driveways, and
// tree lines when planning a flight. Overridable via VITE_MAP_STYLE_URL.
const SATELLITE_STYLE = {
  version: 8,
  sources: {
    'esri-imagery': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 19,
      attribution: 'Imagery © Esri, Maxar, Earthstar Geographics, USDA, USGS',
    },
    'esri-labels': {
      type: 'raster',
      tiles: [
        'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
      ],
      tileSize: 256,
      maxzoom: 19,
    },
  },
  layers: [
    { id: 'imagery', type: 'raster', source: 'esri-imagery' },
    { id: 'labels', type: 'raster', source: 'esri-labels' },
  ],
}

// MapLibre GL preview of a parcel boundary (spec §3.1, §3.3 Parcel Preview).
// Aerial-imagery basemap; the boundary is drawn as a high-contrast fill+line.
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
    const styleUrl = import.meta.env.VITE_MAP_STYLE_URL
    const map = new maplibregl.Map({
      container: ref.current,
      style: styleUrl || SATELLITE_STYLE,
      center: center || [-83.97, 35.75],
      zoom: 18,
      maxZoom: 21
    })
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right')
    map.addControl(new maplibregl.ScaleControl({ unit: 'imperial' }), 'bottom-left')
    mapRef.current = map

    map.on('load', () => {
      if (!geojson) return
      map.addSource('parcel', { type: 'geojson', data: geojson })
      map.addLayer({
        id: 'parcel-fill',
        type: 'fill',
        source: 'parcel',
        paint: { 'fill-color': '#FFD400', 'fill-opacity': 0.12 }
      })
      // Dark casing under a bright line so the boundary reads on any imagery.
      map.addLayer({
        id: 'parcel-line-casing',
        type: 'line',
        source: 'parcel',
        paint: { 'line-color': '#000000', 'line-width': 6, 'line-opacity': 0.5 }
      })
      map.addLayer({
        id: 'parcel-line',
        type: 'line',
        source: 'parcel',
        paint: { 'line-color': '#FFD400', 'line-width': 2.5 }
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
