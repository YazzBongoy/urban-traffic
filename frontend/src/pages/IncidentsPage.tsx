import { AlertTriangle } from 'lucide-react'

export function IncidentsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold tracking-tight">Incidents</h1>
      <div className="rounded-xl border border-gray-800 bg-gray-900/50 p-8 flex flex-col items-center text-center gap-3">
        <AlertTriangle className="h-10 w-10 text-yellow-400" />
        <p className="font-semibold">Module incidents — Phase 2</p>
        <p className="text-sm text-gray-400 max-w-md">
          La détection automatique des incidents (accidents, embouteillages) sera activée avec
          l'intégration vidéo et le moteur d'alertes. Les données de démonstration existent déjà
          en base.
        </p>
      </div>
    </div>
  )
}
