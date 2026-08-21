import { useQuery } from '@tanstack/react-query'
import type { RealtimeTraffic } from '../types'
import { api } from '../services/api'

function congestionColor(level: number): string {
  if (level < 0.33) return 'bg-emerald-400'
  if (level < 0.66) return 'bg-yellow-400'
  return 'bg-red-400'
}

export function ZonesPage() {
  const { data: realtime, isLoading } = useQuery({
    queryKey: ['realtime'],
    queryFn: async () => (await api.get<RealtimeTraffic>('/api/v1/traffic/realtime')).data,
    refetchInterval: 30_000,
  })

  if (isLoading) {
    return <p className="text-sm text-gray-500">Chargement du trafic…</p>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold tracking-tight">
        Trafic en temps réel — {realtime?.total_vehicles.toLocaleString('fr-FR')} véhicules
      </h1>
      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {realtime?.zones.map((zone) => (
          <div key={zone.id} className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <div className="flex items-center justify-between mb-2">
              <h2 className="font-semibold">{zone.name}</h2>
              <span
                className={`text-xs px-2 py-1 rounded-full ${congestionColor(zone.congestion_level)} text-gray-950 font-semibold`}
              >
                {Math.round(zone.congestion_level * 100)} %
              </span>
            </div>
            {zone.description && (
              <p className="text-sm text-gray-400 mb-3 line-clamp-2">{zone.description}</p>
            )}
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-lg bg-gray-950 p-3">
                <dt className="text-xs text-gray-500">Véhicules</dt>
                <dd className="font-semibold mt-1">{zone.vehicle_count}</dd>
              </div>
              <div className="rounded-lg bg-gray-950 p-3">
                <dt className="text-xs text-gray-500">Vitesse moy.</dt>
                <dd className="font-semibold mt-1">{zone.average_speed.toFixed(1)} km/h</dd>
              </div>
            </dl>
          </div>
        ))}
      </div>
      {realtime && realtime.zones.length === 0 && (
        <p className="text-sm text-gray-500">Aucune zone surveillée.</p>
      )}
    </div>
  )
}
