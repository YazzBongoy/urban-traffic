import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  AlertTriangle,
  Car,
  Gauge,
  Video,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Camera, RealtimeTraffic, Statistics } from '../types'
import { api } from '../services/api'

function congestionColor(level: number): string {
  if (level < 0.33) return '#34d399'
  if (level < 0.66) return '#fbbf24'
  return '#f87171'
}

export function DashboardPage() {
  const { data: stats } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => (await api.get<Statistics>('/api/v1/analytics/statistics')).data,
    refetchInterval: 30_000,
  })
  const { data: realtime } = useQuery({
    queryKey: ['realtime'],
    queryFn: async () => (await api.get<RealtimeTraffic>('/api/v1/traffic/realtime')).data,
    refetchInterval: 30_000,
  })
  const { data: cameras } = useQuery({
    queryKey: ['cameras'],
    queryFn: async () => (await api.get<Camera[]>('/api/v1/cameras/')).data,
    refetchInterval: 60_000,
  })

  const onlineCameras = cameras?.filter((c) => c.status === 'online').length ?? 0

  const kpis = [
    { label: 'Caméras en ligne', value: `${onlineCameras}/${cameras?.length ?? 0}`, icon: Video },
    { label: 'Véhicules détectés (24h)', value: stats?.total_vehicles.toLocaleString('fr-FR') ?? '—', icon: Car },
    { label: 'Vitesse moyenne', value: stats ? `${stats.average_speed.toFixed(1)} km/h` : '—', icon: Gauge },
    { label: 'Congestion moyenne', value: realtime ? `${Math.round(realtime.average_congestion * 100)} %` : '—', icon: Activity },
  ]

  const chartData =
    realtime?.zones.map((z) => ({
      name: z.name,
      vehicles: z.vehicle_count,
      congestion: z.congestion_level,
    })) ?? []

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {kpis.map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-400">{label}</span>
              <Icon className="h-4 w-4 text-emerald-400" />
            </div>
            <p className="text-2xl font-bold tracking-tight">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 rounded-xl border border-gray-800 bg-gray-900/50 p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Véhicules par zone</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                <YAxis stroke="#9ca3af" fontSize={12} />
                <Tooltip
                  cursor={{ fill: '#1f2937' }}
                  contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                />
                <Bar dataKey="vehicles" radius={[6, 6, 0, 0]} name="Véhicules">
                  {chartData.map((entry) => (
                    <Cell key={entry.name} fill={congestionColor(entry.congestion)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Niveaux de congestion</h2>
          <div className="space-y-4">
            {realtime?.zones.map((zone) => (
              <div key={zone.id}>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span>{zone.name}</span>
                  <span className="text-gray-400">{zone.average_speed.toFixed(0)} km/h</span>
                </div>
                <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.min(100, Math.max(2, zone.congestion_level * 100))}%`,
                      backgroundColor: congestionColor(zone.congestion_level),
                    }}
                  />
                </div>
              </div>
            ))}
            {realtime && realtime.zones.length === 0 && (
              <p className="text-sm text-gray-500">Aucune zone surveillée.</p>
            )}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-yellow-400/20 bg-yellow-400/5 p-4 flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-yellow-400 shrink-0 mt-0.5" />
        <div className="text-sm text-yellow-200/80">
          Détection d'incidents automatique : disponible en Phase 2 du plan d'implémentation.
        </div>
      </div>
    </div>
  )
}
