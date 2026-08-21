import { useQuery } from '@tanstack/react-query'
import type { Vehicle } from '../types'
import { api } from '../services/api'

export function VehiclesPage() {
  const { data: vehicles, isLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: async () => (await api.get<Vehicle[]>('/api/v1/vehicles/')).data,
  })

  if (isLoading) {
    return <p className="text-sm text-gray-500">Chargement des véhicules…</p>
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold tracking-tight">Véhicules enregistrés ({vehicles?.length ?? 0})</h1>
      <div className="rounded-xl border border-gray-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-900/80 text-gray-400 text-left">
            <tr>
              <th className="px-5 py-3 font-medium">Plaque</th>
              <th className="px-5 py-3 font-medium">Type</th>
              <th className="px-5 py-3 font-medium">Couleur</th>
              <th className="px-5 py-3 font-medium">Propriétaire</th>
              <th className="px-5 py-3 font-medium">Statut</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800 bg-gray-900/30">
            {vehicles?.map((vehicle) => (
              <tr key={vehicle.id} className="hover:bg-gray-900/60">
                <td className="px-5 py-3 font-mono font-semibold">{vehicle.plate_number}</td>
                <td className="px-5 py-3 capitalize">{vehicle.vehicle_type ?? '—'}</td>
                <td className="px-5 py-3 capitalize">{vehicle.color ?? '—'}</td>
                <td className="px-5 py-3">{vehicle.owner_name ?? '—'}</td>
                <td className="px-5 py-3">
                  {vehicle.is_stolen ? (
                    <span className="text-xs px-2 py-1 rounded-full border border-red-400/20 bg-red-400/10 text-red-400">
                      Signalé volé
                    </span>
                  ) : (
                    <span className="text-xs px-2 py-1 rounded-full border border-gray-700 text-gray-400">
                      Normal
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {vehicles && vehicles.length === 0 && (
          <p className="text-sm text-gray-500 p-5">Aucun véhicule enregistré.</p>
        )}
      </div>
    </div>
  )
}
