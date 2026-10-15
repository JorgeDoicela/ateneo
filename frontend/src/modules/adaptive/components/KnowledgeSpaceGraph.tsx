import React, { useState, useEffect, ComponentType } from 'react';
import { createPortal } from 'react-dom';
import { X, Compass, CheckCircle2, Clock, Lock, ArrowDown } from 'lucide-react';
import { adaptiveApi } from '../api/adaptiveApi';
import { useAuth } from '../../../context/AuthContext';
import type { KnowledgeStateResponse } from '../../../types';

export interface KnowledgeSpaceGraphProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NodeStatus {
  label: string;
  icon: ComponentType<{ className?: string }>;
  iconColor: string;
  textColor: string;
}

/**
 * KnowledgeSpaceGraph — Modal institucional de la Ruta de Competencias Clínicas (KST/BKT).
 * Desacoplado del DOM mediante React Portal hacia document.body con overlay backdrop-blur
 * a pantalla completa (z-[100]) para garantizar que cubra tanto la cabecera como la barra inferior móvil.
 */
export default function KnowledgeSpaceGraph({ isOpen, onClose }: KnowledgeSpaceGraphProps) {
  const { user } = useAuth();
  const [data, setData] = useState<KnowledgeStateResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Gestión de cierre con Escape y bloqueo de scroll de la página de fondo
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  // Carga de la topología KST
  useEffect(() => {
    if (!isOpen) return;
    let isMounted = true;
    async function loadGraph() {
      try {
        setLoading(true);
        const res = await adaptiveApi.getKnowledgeState(user?.id);
        if (isMounted) setData(res);
      } catch (err) {
        console.error('Error cargando estado KST:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadGraph();
    return () => { isMounted = false; };
  }, [isOpen, user?.id]);

  if (!isOpen) return null;

  const knowledgeState = data?.knowledge_state || {};
  const nodes = data?.topology?.nodes || [];

  const getNodeStatus = (pVal: number): NodeStatus => {
    if (pVal >= 0.75) {
      return {
        label: 'Dominado',
        icon: CheckCircle2,
        iconColor: 'text-emerald-600',
        textColor: 'text-emerald-700 font-semibold'
      };
    } else if (pVal >= 0.40) {
      return {
        label: 'En Entrenamiento',
        icon: Clock,
        iconColor: 'text-[#0b57d0]',
        textColor: 'text-[#0b57d0] font-semibold'
      };
    } else {
      return {
        label: 'Prerrequisito Pendiente',
        icon: Lock,
        iconColor: 'text-slate-400',
        textColor: 'text-slate-500 font-medium'
      };
    }
  };

  return createPortal(
    <div 
      className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-fadeIn"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="kst-modal-title"
    >
      <div 
        className="bg-white w-full max-w-3xl max-h-[92vh] sm:max-h-[88vh] rounded-[28px] shadow-2xl border border-slate-200/60 flex flex-col animate-scaleUp relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Halos difusos sutiles de fondo para refracción Glassmorphism */}
        <div 
          className="pointer-events-none absolute -top-16 -right-16 w-56 h-56 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />
        <div 
          className="pointer-events-none absolute -bottom-16 -left-16 w-56 h-56 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-2xl"
          aria-hidden="true"
        />

        {/* Cabecera Fija del Modal */}
        <div className="flex items-center justify-between p-5 sm:p-6 pb-4 border-b border-slate-100 shrink-0 relative z-10">
          <div className="flex items-center gap-3">
            <Compass className="w-6 h-6 text-[#0b57d0] shrink-0" />
            <div>
              <h2 id="kst-modal-title" className="text-lg sm:text-xl font-heading font-normal text-slate-900 tracking-tight">
                Ruta de Competencias Clínicas
              </h2>
              <p className="text-xs text-slate-500 mt-0.5 leading-tight">
                Secuencia formativa de prerrequisitos y probabilidad continua de dominio
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer shrink-0"
            title="Cerrar modal"
            aria-label="Cerrar modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Leyenda Clínica Plana */}
        <div className="px-5 sm:px-6 pt-3 pb-2 shrink-0 border-b border-slate-100/60 bg-slate-50/50 relative z-10">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-600">
            <span className="font-semibold text-slate-700">Estados:</span>
            <span className="inline-flex items-center gap-1.5">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
              <span>Dominado (&gt; 75%)</span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-[#0b57d0] shrink-0" />
              <span>En Entrenamiento (40% - 75%)</span>
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span>Prerrequisito Pendiente (&lt; 40%)</span>
            </span>
          </div>
        </div>

        {/* Contenido / Nodos de Competencia con Scroll Limpio */}
        <div className="flex-1 overflow-y-auto no-scrollbar p-5 sm:p-6 space-y-4 relative z-10">
          {loading ? (
            <div className="py-16 text-center text-slate-400 animate-pulse text-xs">
              Cargando ruta formativa y modelo adaptativo de competencias...
            </div>
          ) : nodes.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-400">
              No hay nodos de competencias configurados para esta ruta.
            </div>
          ) : (
            nodes.map((node, idx) => {
              const pVal = knowledgeState[node.id] !== undefined ? knowledgeState[node.id] : 0.40;
              const status = getNodeStatus(pVal);
              const IconComponent = status.icon;

              return (
                <React.Fragment key={node.id}>
                  <div className="p-4 sm:p-5 rounded-[22px] bg-[#f0f4f9]/50 hover:bg-[#f0f4f9]/80 border border-slate-200/70 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
                    <div className="space-y-1 min-w-0 flex-1">
                      <div className="flex items-baseline gap-2">
                        <span className="text-xs font-mono font-bold text-slate-400 shrink-0">
                          0{node.orden || idx + 1}.
                        </span>
                        <h4 className="text-sm sm:text-base font-semibold text-slate-900 tracking-tight">
                          {node.nombre}
                        </h4>
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed">
                        {node.descripcion}
                      </p>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-4 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-200/50">
                      <div className="text-left sm:text-right">
                        <span className="text-[10px] text-slate-400 block font-medium uppercase tracking-wider">
                          Nivel de Dominio
                        </span>
                        <span className="text-base font-mono font-bold text-slate-900">
                          {Math.round(pVal * 100)}%
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5 text-xs shrink-0">
                        <IconComponent className={`w-4 h-4 ${status.iconColor} shrink-0`} />
                        <span className={status.textColor}>
                          {status.label}
                        </span>
                      </div>
                    </div>
                  </div>

                  {idx < nodes.length - 1 && (
                    <div className="flex justify-center -my-1">
                      <ArrowDown className="w-4 h-4 text-slate-300" />
                    </div>
                  )}
                </React.Fragment>
              );
            })
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}
