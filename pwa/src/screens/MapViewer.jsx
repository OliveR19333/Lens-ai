import { useNavigate } from 'react-router-dom'
import { Map as MapIcon, Mountain, Printer } from 'lucide-react'
import { Button, Card, Banner } from '../components/ui'

// Map Viewer (spec §3.3) — view flat map and elevation map per project.
// Map rendering is a Phase 2/3 backend stub; this screen shows the intended
// layout and routes to print/export.
export default function MapViewer() {
  const navigate = useNavigate()
  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Map Viewer</h2>

      <Banner tone="info">
        Map generation (Map 1 flat grid + Map 2 elevation) is implemented as a
        backend stub for Phases 2–3 (spec §9). Wire WebODM + the renderers to
        populate these.
      </Banner>

      <Card>
        <div className="flex items-center gap-2 text-slate-700 font-semibold mb-2">
          <MapIcon size={18} /> Map 1 — Flat Planning Map
        </div>
        <p className="text-sm text-slate-500">
          Grayscale orthomosaic · bold parcel boundary · feature markers · measured
          grid · scale bar + ratio · north arrow · title block (spec §9.1).
        </p>
        <div className="mt-3 aspect-[8.5/11] bg-slate-100 rounded-xl grid place-items-center text-slate-400 text-sm">
          8.5 × 11 preview
        </div>
      </Card>

      <Card>
        <div className="flex items-center gap-2 text-slate-700 font-semibold mb-2">
          <Mountain size={18} /> Map 2 — Elevation Change Map
        </div>
        <p className="text-sm text-slate-500">
          Hillshade · 1 ft / 5 ft contours · slope arrows · spot elevations ·
          grayscale, printer-safe (spec §9.2).
        </p>
        <div className="mt-3 aspect-[8.5/11] bg-slate-100 rounded-xl grid place-items-center text-slate-400 text-sm">
          8.5 × 11 preview
        </div>
      </Card>

      <Button onClick={() => navigate('/print')}>
        <span className="inline-flex items-center justify-center gap-2">
          <Printer size={18} /> Print / Export
        </span>
      </Button>
    </div>
  )
}
