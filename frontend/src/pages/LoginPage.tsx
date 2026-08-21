import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export function LoginPage() {
  const { login, user, loading } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user) {
    navigate('/', { replace: true })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Échec de la connexion')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-center gap-2 mb-8">
          <div className="h-10 w-10 rounded-xl bg-emerald-500 flex items-center justify-center">
            <Activity className="h-6 w-6 text-gray-950" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">UrbanTraffic</h1>
        </div>
        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-gray-800 bg-gray-900/50 p-6 space-y-4"
        >
          <div>
            <label htmlFor="username" className="block text-sm text-gray-400 mb-1.5">
              Identifiant
            </label>
            <input
              id="username"
              type="text"
              required
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2.5 text-sm outline-none focus:border-emerald-500"
              placeholder="admin"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm text-gray-400 mb-1.5">
              Mot de passe
            </label>
            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2.5 text-sm outline-none focus:border-emerald-500"
              placeholder="••••••••"
            />
          </div>
          {error && (
            <p className="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-emerald-500 py-2.5 text-sm font-semibold text-gray-950 hover:bg-emerald-400 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {submitting && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-gray-900/40 border-t-gray-900" />
            )}
            Se connecter
          </button>
        </form>
      </div>
    </div>
  )
}
