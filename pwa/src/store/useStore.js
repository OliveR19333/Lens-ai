import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Global app state (spec §3.1 — Zustand). Auth token + lightweight UI state are
// persisted to localStorage for a persistent field session (spec §3.3 Login).
export const useStore = create(
  persist(
    (set, get) => ({
      // --- auth ---
      token: null,
      username: null,
      setAuth: (token, username) => set({ token, username }),
      logout: () => set({ token: null, username: null }),
      isAuthenticated: () => !!get().token,

      // --- connectivity ---
      online: typeof navigator !== 'undefined' ? navigator.onLine : true,
      setOnline: (online) => set({ online }),

      // --- current mission draft ---
      draft: {
        address: '',
        geocode: null, // { lat, lng, county, county_name }
        parcel: null, // GeoJSON + metadata
        mission: null // { mission_id, summary, kmz_url }
      },
      setDraft: (patch) => set({ draft: { ...get().draft, ...patch } }),
      resetDraft: () =>
        set({ draft: { address: '', geocode: null, parcel: null, mission: null } }),

      // --- county cache status (mirrors backend /counties) ---
      counties: [],
      setCounties: (counties) => set({ counties }),

      // --- offline write queue depth (for the sync badge) ---
      queueDepth: 0,
      setQueueDepth: (queueDepth) => set({ queueDepth })
    }),
    {
      name: 'gas-mapping',
      partialize: (s) => ({ token: s.token, username: s.username })
    }
  )
)
