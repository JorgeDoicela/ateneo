import { WifiOff, RefreshCw } from 'lucide-react';
import { useConnectivitySync } from '../../storage/useConnectivitySync';

/**
 * ConnectivityBadge — Indicador de red clínica y sincronización offline en segundo plano
 */
export default function ConnectivityBadge() {
  const { isOnline, isSyncing, pendingCount, syncPendingEvaluations } = useConnectivitySync();

  if (!isOnline) {
    return (
      <div 
        className="flex items-center gap-1.5 text-amber-700 font-medium px-2 py-1"
        title="Sin conexión de red hospitalaria. Modo local activo con buffer seguro."
      >
        <WifiOff className="w-3.5 h-3.5 text-amber-600 shrink-0" />
        <span className="hidden sm:inline">Modo Local</span>
      </div>
    );
  }

  if (pendingCount > 0) {
    return (
      <button
        onClick={() => syncPendingEvaluations()}
        disabled={isSyncing}
        className="flex items-center gap-1.5 text-indigo-700 hover:text-indigo-900 transition-colors font-medium px-2 py-1 cursor-pointer"
        title="Sincronizar evaluaciones pendientes con el clúster central"
      >
        <RefreshCw className={`w-3.5 h-3.5 text-indigo-600 ${isSyncing ? 'animate-spin' : ''}`} />
        <span>{pendingCount} pendiente{pendingCount > 1 ? 's' : ''}</span>
      </button>
    );
  }

  return null;
}
