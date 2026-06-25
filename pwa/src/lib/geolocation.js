// Device GPS — works fully offline (the phone's GPS chip needs no internet).
// This is the field-friendly way to locate the property: stand on it, tap
// "Use my location", and look the parcel up against cached data.
export function getCurrentPosition(options = {}) {
  return new Promise((resolve, reject) => {
    if (!('geolocation' in navigator)) {
      reject(new Error('Geolocation is not available on this device.'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          accuracy: pos.coords.accuracy
        }),
      (err) => reject(new Error(err.message || 'Could not get your location.')),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000, ...options }
    )
  })
}
