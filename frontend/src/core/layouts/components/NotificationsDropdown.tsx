import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Bell, CheckCheck, BookOpen, Sparkles, Users, X } from 'lucide-react';

export interface NotificationsDropdownProps {
  dropUp?: boolean;
  showLabel?: boolean;
}

interface NotificationItem {
  id: string;
  titulo: string;
  mensaje: string;
  tiempo: string;
  leido: boolean;
  tipo: 'evaluacion' | 'normativa' | 'sala';
}

const NOTIFICACIONES_MOCK: NotificationItem[] = [
  {
    id: 'notif-1',
    titulo: 'Debriefing Socrático Disponible',
    mensaje: 'La retroalimentación formativa del caso clínico de preeclampsia está lista para revisión.',
    tiempo: 'Hace 10 min',
    leido: false,
    tipo: 'evaluacion'
  },
  {
    id: 'notif-2',
    titulo: 'Actualización Normativa GPC',
    mensaje: 'Nuevos criterios de severidad hemodinámica anclados a la GPC Ecuador.',
    tiempo: 'Hace 2 horas',
    leido: false,
    tipo: 'normativa'
  },
  {
    id: 'notif-3',
    titulo: 'Sesión Clínica Finalizada',
    mensaje: 'El dictamen del caso grupal en AteneoRoom ha sido sincronizado a tu desempeño.',
    tiempo: 'Ayer',
    leido: true,
    tipo: 'sala'
  }
];

/**
 * NotificationsDropdown — Modal centrado de notificaciones clínicas formativas
 * Renderizado vía React Portal hacia document.body con overlay backdrop-blur.
 */
export default function NotificationsDropdown({ showLabel = false }: NotificationsDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [notificaciones, setNotificaciones] = useState<NotificationItem[]>(NOTIFICACIONES_MOCK);

  const sinLeerCount = notificaciones.filter(n => !n.leido).length;

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const marcarTodasLeidas = () => {
    setNotificaciones(prev => prev.map(n => ({ ...n, leido: true })));
  };

  const marcarLeida = (id: string) => {
    setNotificaciones(prev => prev.map(n => n.id === id ? { ...n, leido: true } : n));
  };

  const getIconoTipo = (tipo: NotificationItem['tipo']) => {
    switch (tipo) {
      case 'evaluacion':
        return <Sparkles className="w-5 h-5 text-[#0b57d0] shrink-0" />;
      case 'normativa':
        return <BookOpen className="w-5 h-5 text-[#2563eb] shrink-0" />;
      case 'sala':
        return <Users className="w-5 h-5 text-[#7c3aed] shrink-0" />;
    }
  };

  return (
    <div>
      {showLabel ? (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex flex-col items-center justify-center py-1 px-1.5 text-slate-700 hover:text-[#0b57d0] active:scale-95 transition-all cursor-pointer group select-none relative"
          title="Notificaciones Clínicas"
          aria-expanded={isOpen}
          aria-label="Abrir panel de notificaciones"
        >
          <div className="relative">
            <Bell className="w-5 h-5 text-slate-700 group-hover:text-[#0b57d0] transition-colors" />
            {sinLeerCount > 0 && (
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#0b57d0] ring-2 ring-white" />
            )}
          </div>
          <span className="text-[11px] font-medium text-slate-600 group-hover:text-[#0b57d0] transition-colors mt-1 leading-none">
            Notificaciones
          </span>
        </button>
      ) : (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="p-2 rounded-full text-slate-700 hover:text-[#0b57d0] hover:bg-slate-100 transition-colors relative cursor-pointer"
          title="Notificaciones Clínicas"
          aria-expanded={isOpen}
          aria-label="Abrir panel de notificaciones"
        >
          <Bell className="w-5 h-5 text-[#0b57d0]" />
          {sinLeerCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#0b57d0] ring-2 ring-white" />
          )}
        </button>
      )}

      {isOpen && createPortal(
        <div 
          className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
          onClick={() => setIsOpen(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="notif-modal-title"
        >
          <div 
            className="bg-white rounded-[28px] shadow-2xl border border-slate-200/60 max-w-lg w-full p-6 sm:p-8 space-y-5 animate-scaleUp relative overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Halos difusos sutiles de fondo para refracción Glassmorphism */}
            <div 
              className="pointer-events-none absolute -top-12 -right-12 w-52 h-52 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
              aria-hidden="true"
            />
            <div 
              className="pointer-events-none absolute -bottom-10 -left-10 w-52 h-52 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
              aria-hidden="true"
            />

            {/* Cabecera del Diálogo */}
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 relative z-10">
              <div className="flex items-center gap-2.5">
                <Bell className="w-5 h-5 text-blue-600 shrink-0" />
                <div>
                  <h3 id="notif-modal-title" className="text-lg font-heading font-normal text-slate-900 tracking-tight">
                    Notificaciones Clínicas
                  </h3>
                  <p className="text-xs text-slate-500">
                    Novedades formativas, debriefings y actualizaciones normativas
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer transition-colors"
                aria-label="Cerrar modal de notificaciones"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Barra de Estado y Acciones Rápidas */}
            <div className="flex items-center justify-between pt-1 relative z-10">
              <span className="text-xs font-semibold text-slate-700">
                {sinLeerCount > 0 ? `${sinLeerCount} novedades pendientes` : 'Todas las notificaciones leídas'}
              </span>
              {sinLeerCount > 0 && (
                <button
                  type="button"
                  onClick={marcarTodasLeidas}
                  className="text-xs text-[#0b57d0] hover:underline flex items-center gap-1 cursor-pointer font-medium"
                >
                  <CheckCheck className="w-4 h-4" />
                  <span>Marcar todas como leídas</span>
                </button>
              )}
            </div>

            {/* Lista de Notificaciones Formativas */}
            <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto no-scrollbar relative z-10">
              {notificaciones.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  No tienes notificaciones pendientes
                </div>
              ) : (
                notificaciones.map(item => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => marcarLeida(item.id)}
                    className={`w-full text-left py-3 px-3 rounded-2xl transition-all flex items-start gap-3 cursor-pointer ${
                      item.leido ? 'hover:bg-slate-50 opacity-75' : 'bg-slate-50/70 hover:bg-slate-100/80 shadow-2xs'
                    }`}
                  >
                    <div className="mt-0.5 shrink-0">
                      {getIconoTipo(item.tipo)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <p className={`text-xs ${item.leido ? 'font-medium text-slate-700' : 'font-semibold text-[#1f1f1f]'}`}>
                          {item.titulo}
                        </p>
                        <span className="text-[10px] text-slate-400 shrink-0">{item.tiempo}</span>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                        {item.mensaje}
                      </p>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  );
}
