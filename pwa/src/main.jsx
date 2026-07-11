import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { useStore } from './store/useStore'
import { drainQueue, queueDepth } from './db/parcelCache'
import { createProject } from './api/client'

// Track connectivity and fire the offline-queue drain on reconnect
// (spec §3.2 auto-sync trigger / §10.1 queued project creation).
function wireConnectivity() {
  const set = (online) => useStore.getState().setOnline(online)
  window.addEventListener('online', async () => {
    set(true)
    const depth = await drainQueue(async (item) => {
      if (item.type === 'createProject') await createProject(item.payload)
    })
    useStore.getState().setQueueDepth(depth)
  })
  window.addEventListener('offline', () => set(false))
  queueDepth().then((d) => useStore.getState().setQueueDepth(d))
}
wireConnectivity()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
