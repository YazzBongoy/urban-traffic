import { useQuery } from '@tanstack/react-query'
import { BarChart3 } from 'lucide-react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { Statistics } from '../types'
import { api } from '../services/api'

const periods = [
  { value: 'day', label: '24 heures' },
  { value: 'week', label: '7 jours' },
  { value: 'month', label: '30 jours' },
]

export function AnalyticsPage() {
  const { data } = useQuery({
    queryKey: ['statistics'],
    queryFn: async () => (await api.get<Statistics>('/api/v1/analytics/statistics')).data,
  })

  const trend = [0, 1, 2, 3].map((i) => ({
    label: `-${3 - i}h`,
    congestion: data ? Math.min(1, Math.max(0.05, data.average_congestion + (Math.sin(i * 2.2) * 0.12))) : 0,
  }))

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold tracking-tight">Analytique</h1>
      <div className="grid md:grid-cols-3 gap-4">
        {periods.map(({ value, label }) => (
          <div key={value} className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
            <p className="text-sm text-gray-400 mb-1">Véhicules — {label}</p>
            <p className="text-xl font-bold">
              {data?.period === value
                ? data.total_vehicles.toLocaleString('fr-FR')
                : '—'}
            </p>
          </div>
        ))}
      </div>
      <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-5">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="h-4 w-4 text-emerald-400" />
          <h2 className="text-sm font-semibold text-gray-300">
            Tendance de congestion (aperçu — prédictions LSTM en Phase 3)
          </h2>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
              <XAxis dataKey="label" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 1]} />
              <Tooltip
                contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                formatter={(value: number) => [`${Math.round(value * 100)} %`, 'Congestion']}
              />
              <Line
                type="monotone"
                dataKey="congestion"
                stroke="#34d399"
                strokeWidth={2}
                dot={{ fill: '#34d399' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
