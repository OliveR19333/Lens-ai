// DJI Fly handoff (spec §3.4).
//
// Full programmatic DJI Fly deep-linking is not publicly documented, so the
// reliable path is the iOS share sheet. We share a KMZ that was generated
// locally on the phone (offline), falling back to a download if the Web Share
// API can't take files.
import { kmzUrl } from '../api/client'

function downloadBlob(blob, filename) {
  const objUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  // Delay revoke so Safari/Chrome don't cancel the in-flight download.
  setTimeout(() => URL.revokeObjectURL(objUrl), 2000)
  return { method: 'download' }
}

async function shareBlob(blob, filename) {
  const file = new File([blob], filename, { type: 'application/vnd.google-earth.kmz' })
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent || '')

  // On a phone, the share sheet (AirDrop / Save to Files) is the useful path.
  // On desktop it tends to be a dead end, so just download to disk — which is
  // also exactly where the Mac installer looks for the file.
  if (isMobile && navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({ files: [file], title: 'DJI Waypoint Mission' })
      return { method: 'share-sheet' }
    } catch (e) {
      if (e && e.name === 'AbortError') return { method: 'cancelled' }
      // Any other share failure → fall back to a direct download.
    }
  }

  return downloadBlob(blob, filename)
}

// Share a KMZ generated on-device (offline path — preferred in the field).
export async function shareMissionBlob(kmzBlob, name = 'mission') {
  return shareBlob(kmzBlob, `${name}.kmz`)
}

// Share a KMZ that lives on the backend (online path — fetches first).
export async function shareMissionKmz(missionId, token) {
  const res = await fetch(kmzUrl(missionId), {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  if (!res.ok) throw new Error(`Failed to fetch KMZ (${res.status})`)
  const blob = await res.blob()
  return shareBlob(blob, `mission-${missionId}.kmz`)
}
