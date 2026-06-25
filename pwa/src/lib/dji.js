// DJI Fly handoff (spec §3.4).
//
// Full programmatic DJI Fly deep-linking is not publicly documented, so the
// reliable path is the iOS share sheet. We share a KMZ that was generated
// locally on the phone (offline), falling back to a download if the Web Share
// API can't take files.
import { kmzUrl } from '../api/client'

async function shareBlob(blob, filename) {
  const file = new File([blob], filename, { type: 'application/vnd.google-earth.kmz' })

  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    await navigator.share({
      files: [file],
      title: 'DJI Waypoint Mission',
      text: 'Open in DJI Fly to import this mapping mission.'
    })
    return { method: 'share-sheet' }
  }

  const objUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(objUrl)
  return { method: 'download' }
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
