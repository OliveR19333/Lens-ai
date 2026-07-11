import { useState } from 'react'
import { Card, Field, Banner, Button } from '../components/ui'

// Print / Export (spec §3.3, §9.3) — scale selector → PDF → share sheet.
// The locked best-fit scale is computed on the backend; this screen lets the
// operator confirm it and shows the proportional enlargement note.
export default function PrintExport() {
  // Demo defaults mirroring the spec §9.3 worked example (300×400 ft → 1"=40ft).
  const [feetPerInch, setFeetPerInch] = useState(40)
  const enlargement = (25 / 8.5).toFixed(2)

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-slate-800">Print / Export</h2>

      <Card>
        <Field
          label={`Scale: 1 inch = ${feetPerInch} feet`}
          hint="Auto-fit to 8.5×11 with 0.5″ margins, rounded to nearest 5 ft (spec §9.3)."
        >
          <input
            type="range"
            min="5"
            max="200"
            step="5"
            value={feetPerInch}
            onChange={(e) => setFeetPerInch(Number(e.target.value))}
            className="w-full"
          />
        </Field>

        <Banner tone="info">
          Scale: 1 inch = {feetPerInch} feet — Enlarge {enlargement}× for 25×30 grid paper.
        </Banner>
      </Card>

      <Card>
        <h3 className="font-semibold text-slate-700 mb-1">Export</h3>
        <p className="text-sm text-slate-500 mb-3">
          PDF generation runs on the backend at ≥300 DPI (spec §9.4, §10.2 —
          requires connectivity). Exported PDFs route through the iOS share sheet.
        </p>
        <div className="grid grid-cols-2 gap-3">
          <Button variant="secondary" disabled>Map 1 PDF</Button>
          <Button variant="secondary" disabled>Map 2 PDF</Button>
        </div>
        <p className="text-xs text-slate-400 mt-2">Enabled once maps are rendered (Phase 2/3).</p>
      </Card>
    </div>
  )
}
