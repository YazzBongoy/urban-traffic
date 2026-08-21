import { useQuery } from '@tanstack/react-query'
import { MapPin, Radio } from 'lucide-react'
import type { Camera, CameraStatus } from '../types'
import { api } from '../services/api'

const statusStyles: Record<CameraStatus, string> = {
  online: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  offline: 'bg-red-400/10 text-red-400 border-red-400/20',
  maintenance: 'bg-yellow-400/10 text-yellow-400 border-yellow-400/20',
}

const statusLabels: Record<CameraStatus, string> = {
  online: 'En ligne',
  offline: 'Hors ligne',
  maintenance: 'Maintenance',
}

export function CamerasPage() {
  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: async () => (await api.get<Camera[]>('/api/v1/cameras/')).data,
    refetchInterval: 60_000,
  })

  if (isLoading) {
    return <p className="text-sm text-gray-500">Chargement des caméras…</p>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold tracking-tight">Caméras ({cameras?.length ?? 0})</h1>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {cameras?.map((camera) => (
          <div key={camera.id} className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <div className="flex items-start justify-between mb-3">
              <div>
                <p className="font-semibold">{camera.name}</p>
                <p className="text-sm text-gray-400 flex items-center gap-1 mt-1">
                  <MapPin className="h-3.5 w-3.5" />
                  {camera.location}
                </p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded-full border ${statusStyles[camera.status]}`}
              >
                {statusLabels[camera.status]}
              </span>
            </div>
            <dl className="text-sm space-y-1.5 text-gray-400">
              <div className="flex justify-between gap-2">
                <dt>Coordonnées</dt>
                <dd className="text-gray-300 font-mono text-xs">
                  {camera.latitude.toFixed(4)}, {camera.longitude.toFixed(4)}
                </dd>
              </div>
              <div className="flex justify-between gap-2">
                <dt>Caméra 360°</dt>
                <dd>{camera.is_360 ? 'Oui' : 'Non'}</dd>
              </div>
              <div className="flex justify-between items-center gap-2">
                <dt>Flux RTSP</dt>
                <dd className="text-gray-300 flex items-center gap-1 truncate max-w-[180px]">
                  <Radio className="h-3 w-3 shrink-0" />
                  <span className="truncate font-mono text-xs">{camera.rtsp_url}</span>
                </dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
      {cameras && cameras.length === 0 && (
        <p className="text-sm text-gray-500">Aucune caméra enregistrée.</p>
      )}
    </div>
  )
}
