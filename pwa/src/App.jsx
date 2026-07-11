import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import { useStore } from './store/useStore'

import Login from './screens/Login'
import Dashboard from './screens/Dashboard'
import NewMission from './screens/NewMission'
import ParcelPreview from './screens/ParcelPreview'
import MissionOutput from './screens/MissionOutput'
import UploadImages from './screens/UploadImages'
import MapViewer from './screens/MapViewer'
import PrintExport from './screens/PrintExport'
import History from './screens/History'
import Annotate from './screens/Annotate'
import Settings from './screens/Settings'

// Route guard — redirect to /login when unauthenticated (spec §3.3).
function Protected({ children }) {
  const token = useStore((s) => s.token)
  const location = useLocation()
  if (!token) return <Navigate to="/login" replace state={{ from: location }} />
  return <Layout>{children}</Layout>
}

// Screen flow mirrors spec §3.3.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/new" element={<Protected><NewMission /></Protected>} />
      <Route path="/parcel" element={<Protected><ParcelPreview /></Protected>} />
      <Route path="/mission" element={<Protected><MissionOutput /></Protected>} />
      <Route path="/upload" element={<Protected><UploadImages /></Protected>} />
      <Route path="/maps" element={<Protected><MapViewer /></Protected>} />
      <Route path="/print" element={<Protected><PrintExport /></Protected>} />
      <Route path="/history" element={<Protected><History /></Protected>} />
      <Route path="/annotate" element={<Protected><Annotate /></Protected>} />
      <Route path="/settings" element={<Protected><Settings /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
