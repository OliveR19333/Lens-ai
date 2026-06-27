import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store/useStore'
import { login } from '../api/client'
import { Button, Field, TextInput, Banner } from '../components/ui'

// Login screen (spec §3.3) — JWT auth, persistent session.
export default function Login() {
  const navigate = useNavigate()
  const setAuth = useStore((s) => s.setAuth)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      const { access_token } = await login(username, password)
      setAuth(access_token, username)
      navigate('/')
    } catch {
      setError('Invalid username or password.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-full bg-slate-950 flex flex-col justify-center px-6 py-12">
      <div className="text-center mb-8">
        <img src="/logo.png" alt="Teaster's Natural Creations" className="w-40 h-40 mx-auto mb-3 rounded-2xl" />
        <h1 className="text-white text-2xl font-bold">TNC GAS Mapping</h1>
        <p className="text-gas-blue text-sm mt-1">Ground &amp; Aerial Services · Teasters</p>
      </div>

      <form onSubmit={onSubmit} className="bg-white rounded-2xl p-6 shadow-lg">
        {error && (
          <div className="mb-4">
            <Banner tone="error">{error}</Banner>
          </div>
        )}
        <Field label="Username">
          <TextInput
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoCapitalize="none"
            autoComplete="username"
            required
          />
        </Field>
        <Field label="Password">
          <TextInput
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </Field>
        <Button type="submit" disabled={busy}>
          {busy ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
    </div>
  )
}
