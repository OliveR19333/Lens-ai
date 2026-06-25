// DJI Fly handoff (spec §3.4).
//
// Full programmatic DJI Fly deep-linking is not publicly documented, so the
// reliable path is the iOS share sheet: fetch the KMZ, then invoke the native
// Web Share API (with a file). The user picks "Copy to DJI Fly" or saves to the
// Files app and imports manually.
import { kmzUrl } from '../api/client'

export async function shareMissionKmz(missionId, token) {
  const url = kmzUrl(missionId)
  const res = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
  if (!res.ok) throw new Error(`Failed to fetch KMZ (${res.status})`)
  const blob = await res.blob()
  const file = new File([blob], `mission-${missionId}.kmz`, {
    type: 'application/vnd.google-earth.kmz'
  })

  // Preferred: native share sheet with the file attached (iOS Safari).
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    await navigator.share({
      files: [file],
      title: 'DJI Waypoint Mission',
      text: 'Open in DJI Fly to import this mapping mission.'
    })
    return { method: 'share-sheet' }
  }

  // Fallback: trigger a download so the user can save to Files → DJI Fly.
  const objUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objUrl
  a.download = file.name
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(objUrl)
  return { method: 'download' }
}
