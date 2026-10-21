import { useState, useEffect, useMemo, useContext } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientContext, useQuery } from '@tanstack/react-query';
import { 
  Bell, 
  CheckCheck, 
  BookOpen, 
  Sparkles, 
  Users, 
  X, 
  Download,
  Activity,
  ClipboardCheck,
  CheckCircle2,
  Award,
  ArrowRight
} from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import { studyPlanApi } from '../../../modules/study_plans/api/studyPlanApi';
import { assessmentApi } from '../../../modules/assessments/api/assessmentApi';
import { usePWAInstall } from '../../pwa/usePWAInstall';
import PWAInstallModal from '../../pwa/PWAInstallModal';

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

interface SmartDiagnosticNotification {
  stateKey: string;
  badge: string;
  title: string;
  description: string;
  actionLabel: string;
  actionUrl: string;
  progress?: number;
  completedTasks?: number;
  totalTasks?: number;
  type: 'pre_test' | 'plan_in_progress' | 'post_test_ready' | 'cycle_completed';
}

const STORAGE_PWA_NOTIF_READ = 'ateneo_pwa_notif_read';

// Cliente de fallback silencioso para testing o renders fuera de QueryClientProvider
const fallbackQueryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false, gcTime: 0, staleTime: Infinity, enabled: false }
  }
});

/**
 * NotificationsDropdown — Modal de notificaciones clínicas y formativas inteligentes
 * Renderizado vía React Portal hacia document.body con overlay backdrop-blur.
 * Integra de forma dinámica e inteligente el ciclo formativo: Pre-Test -> Plan Prescriptivo -> Post-Test.
 */
export default function NotificationsDropdown({ showLabel = false }: NotificationsDropdownProps) {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [notificaciones, setNotificaciones] = useState<NotificationItem[]>([]);
  const { isInstalled, promptInstall, showIOSModal, setShowIOSModal } = usePWAInstall();

  const queryContext = useContext(QueryClientContext);
  const effectiveClient = queryContext || fallbackQueryClient;
  const isClientReady = !!queryContext;

  const [isPWANotifRead, setIsPWANotifRead] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(STORAGE_PWA_NOTIF_READ) === 'true';
  });


  // Consulta del plan de estudio prescriptivo activo (solo para estudiantes con context listo)
  const { data: activePlan, isLoading: loadingPlan } = useQuery({
    queryKey: ['activeStudyPlan'],
    queryFn: studyPlanApi.getMyActivePlan,
    enabled: isClientReady && user?.rol === 'alumno',
    staleTime: 1000 * 60 * 2,
  }, effectiveClient);

  // Consulta del historial de evaluaciones diagnósticas (solo para estudiantes con context listo)
  const { data: history = [], isLoading: loadingHistory } = useQuery({
    queryKey: ['myAssessmentsHistory'],
    queryFn: assessmentApi.getMyHistory,
    enabled: isClientReady && user?.rol === 'alumno',
    staleTime: 1000 * 60 * 2,
  }, effectiveClient);

  // Síntesis inteligente del estado formativo del alumno
  const smartNotif = useMemo<SmartDiagnosticNotification | null>(() => {
    if (user?.rol !== 'alumno') return null;
    if (loadingPlan || loadingHistory) return null;

    // 1. Estado Plan Activo en Curso
    if (activePlan && activePlan.status === 'active') {
      const totalTasks = activePlan.tasks?.length || 0;
      const completedTasks = activePlan.tasks?.filter((t) => t.is_completed).length || 0;
      const isUnlockedPostTest = activePlan.progress_percentage >= 100 || (totalTasks > 0 && completedTasks === totalTasks);

      if (isUnlockedPostTest) {
        return {
          stateKey: `smart_posttest_${activePlan.id}`,
          badge: 'Hito Formativo Desbloqueado',
          title: 'Post-Test Isomórfico Disponible',
          description: 'Completaste las actividades de tu plan de refuerzo. Rinde la evaluación de cierre para certificar formalmente tu factor de Ganancia de Hake (g).',
          actionLabel: 'Rendir Post-Test Isomórfico',
          actionUrl: '/analytics',
          type: 'post_test_ready',
        };
      }

      return {
        stateKey: `smart_plan_${activePlan.id}_${completedTasks}_${totalTasks}`,
        badge: 'Plan Prescriptivo Activo',
        title: activePlan.title || 'Plan de Refuerzo Clínico Prioritario',
        description: `Nivelación en curso: ${completedTasks} de ${totalTasks} actividades formativas completadas. Continúa tus simulaciones y lecturas normativas asignadas.`,
        actionLabel: 'Continuar Plan de Estudio',
        actionUrl: '/analytics',
        progress: activePlan.progress_percentage,
        completedTasks,
        totalTasks,
        type: 'plan_in_progress',
      };
    }

    // 2. Estado Ciclo previo completado con Ganancia de Hake (sin plan activo)
    const lastCompletedPostTest = history.find(
      (a) => a.assessment_type === 'post_test' && a.status === 'completed' && a.hake_gain_g !== null && a.hake_gain_g !== undefined
    );
    if (lastCompletedPostTest && lastCompletedPostTest.hake_gain_g !== null && lastCompletedPostTest.hake_gain_g !== undefined) {
      return {
        stateKey: `smart_cycle_${lastCompletedPostTest.id}`,
        badge: 'Ciclo Diagnóstico Certificado',
        title: 'Factor de Ganancia de Hake Registrado',
        description: `Tu última evaluación formativa certificó una ganancia de aprendizaje g = ${lastCompletedPostTest.hake_gain_g.toFixed(2)}. Puedes consultar el desglose o iniciar un nuevo diagnóstico.`,
        actionLabel: 'Ver Analítica y Nuevo Ciclo',
        actionUrl: '/analytics',
        type: 'cycle_completed',
      };
    }

    // 3. Estado Inicial: Estudiante sin Pre-Test completado
    const hasCompletedPreTest = history.some(
      (a) => a.assessment_type === 'pre_test' && a.status === 'completed'
    );
    if (!hasCompletedPreTest) {
      return {
        stateKey: 'smart_pretest_initial',
        badge: 'Evaluación Diagnóstica CACES',
        title: 'Pre-Test Diagnóstico Pendiente',
        description: 'Rinde la batería troncal de 4 casos clínicos para evaluar tu nivel basal y estructurar tu plan de refuerzo prescriptivo en tu Zona de Desarrollo Próximo.',
        actionLabel: 'Iniciar Pre-Test CACES',
        actionUrl: '/analytics',
        type: 'pre_test',
      };
    }

    return null;
  }, [user?.rol, loadingPlan, loadingHistory, activePlan, history]);

  const isPWAPending = !isInstalled && !isPWANotifRead;
  const isSmartActive = !!smartNotif;
  const sinLeerCount = notificaciones.filter(n => !n.leido).length + (isPWAPending ? 1 : 0) + (isSmartActive ? 1 : 0);

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
    setIsPWANotifRead(true);
    localStorage.setItem(STORAGE_PWA_NOTIF_READ, 'true');
  };

  const handleInstallClick = async () => {
    setIsPWANotifRead(true);
    localStorage.setItem(STORAGE_PWA_NOTIF_READ, 'true');
    const outcome = await promptInstall();
    if (outcome === 'accepted' || outcome === 'guide_shown') {
      setIsOpen(false);
    }
  };

  const handleSmartNotifClick = (item: SmartDiagnosticNotification) => {
    setIsOpen(false);
    navigate(item.actionUrl);
  };

  const marcarLeida = (id: string) => {
    setNotificaciones(prev => prev.map(n => n.id === id ? { ...n, leido: true } : n));
  };

  const getSmartIcon = (tipo: SmartDiagnosticNotification['type']) => {
    switch (tipo) {
      case 'pre_test':
        return <ClipboardCheck className="w-5 h-5 text-[#0b57d0] shrink-0" />;
      case 'plan_in_progress':
        return <Activity className="w-5 h-5 text-[#0b57d0] shrink-0" />;
      case 'post_test_ready':
        return <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />;
      case 'cycle_completed':
        return <Award className="w-5 h-5 text-[#0b57d0] shrink-0" />;
    }
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
                {sinLeerCount > 0 
                  ? `${sinLeerCount} novedad${sinLeerCount > 1 ? 'es' : ''} pendiente${sinLeerCount > 1 ? 's' : ''}` 
                  : notificaciones.length > 0 || smartNotif
                    ? 'Todas las notificaciones leídas' 
                    : 'Bandeja al día'}
              </span>
              {(notificaciones.some(n => !n.leido) || isPWAPending) && (
                <button
                  type="button"
                  onClick={marcarTodasLeidas}
                  className="text-xs text-[#0b57d0] hover:underline flex items-center gap-1 cursor-pointer font-medium"
                >
                  <CheckCheck className="w-4 h-4" />
                  <span>Marcar avisos como leídos</span>
                </button>
              )}
            </div>

            {/* Lista de Notificaciones Formativas */}
            <div className="space-y-3 max-h-80 overflow-y-auto no-scrollbar relative z-10">
              {/* 1. Notificación Inteligente Formativa (Pre-Test / Plan / Post-Test) */}
              {smartNotif && (
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => handleSmartNotifClick(smartNotif)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSmartNotifClick(smartNotif);
                    }
                  }}
                  className="w-full text-left p-4 rounded-2xl border transition-all cursor-pointer group active:scale-[0.99] select-none bg-gradient-to-br from-blue-50/80 via-indigo-50/50 to-white border-blue-200/90 shadow-2xs hover:border-blue-300"
                >
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 shrink-0">
                      {getSmartIcon(smartNotif.type)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[10px] font-semibold tracking-wider uppercase text-blue-700">
                          {smartNotif.badge}
                        </span>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className="w-2 h-2 rounded-full bg-[#0b57d0] ring-2 ring-white" />
                          <span className="text-[10px] font-semibold text-blue-700">Formativo</span>
                        </div>
                      </div>

                      <h4 className="text-xs sm:text-sm mt-0.5 font-semibold text-slate-900 group-hover:text-[#0b57d0] transition-colors">
                        {smartNotif.title}
                      </h4>

                      <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
                        {smartNotif.description}
                      </p>

                      {smartNotif.progress !== undefined && (
                        <div className="space-y-1.5 mt-2.5 max-w-md">
                          <div className="flex justify-between text-[10px] font-medium text-slate-500">
                            <span>Progreso de Nivelación</span>
                            <span className="font-semibold text-blue-700">{Math.round(smartNotif.progress)}%</span>
                          </div>
                          <div className="w-full bg-slate-200/80 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-blue-600 to-indigo-600 h-1.5 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min(100, Math.max(0, smartNotif.progress))}%` }}
                            />
                          </div>
                        </div>
                      )}

                      <div className="mt-3 flex items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#0b57d0] group-hover:bg-blue-700 text-white font-medium text-xs shadow-xs transition-colors">
                          <span>{smartNotif.actionLabel}</span>
                          <ArrowRight className="w-3.5 h-3.5 text-white" />
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* 2. Notificación Dinámica de Instalación PWA */}
              {!isInstalled && (
                <button
                  type="button"
                  onClick={handleInstallClick}
                  className={`w-full text-left p-3.5 rounded-2xl border transition-all flex items-start gap-3 cursor-pointer group active:scale-[0.99] select-none ${
                    isPWANotifRead
                      ? 'bg-slate-50/70 hover:bg-slate-100/80 border-slate-200/60 opacity-80'
                      : 'bg-gradient-to-r from-blue-50/70 via-indigo-50/40 to-cyan-50/60 hover:from-blue-100/80 hover:via-indigo-100/60 hover:to-cyan-100/80 border-blue-200/80 shadow-2xs'
                  }`}
                  title="Tocar o hacer clic para instalar la aplicación"
                >
                  <Download className="w-5 h-5 text-[#0b57d0] shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className={`text-xs ${isPWANotifRead ? 'font-medium text-slate-700' : 'font-semibold text-slate-900 group-hover:text-[#0b57d0] transition-colors'}`}>
                        Instalar Ateneo+ en este dispositivo
                      </p>
                      <span className="text-[11px] font-semibold text-[#0b57d0] shrink-0">
                        App PWA
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
                      Instala la aplicación médica para acceso hospitalario directo y simulación clínica a pantalla completa.
                    </p>
                    <div className="mt-2.5 flex items-center gap-2">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#0b57d0] group-hover:bg-blue-700 text-white font-medium text-xs shadow-xs transition-colors">
                        <Download className="w-3.5 h-3.5 text-white" />
                        <span>Instalar ahora</span>
                      </span>
                    </div>
                  </div>
                </button>
              )}

              {/* 3. Notificaciones Formativas Clínicas Estándar */}
              {notificaciones.length === 0 && !smartNotif && isInstalled ? (
                <div className="py-12 px-4 flex flex-col items-center justify-center text-center">
                  <Bell className="w-8 h-8 text-slate-300 stroke-[1.5] mb-2.5" />
                  <p className="text-sm font-medium text-slate-700">Sin notificaciones pendientes</p>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
                    Aquí se mostrarán avisos de debriefings clínicos, salas colaborativas y actualizaciones de GPC.
                  </p>
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

      {/* Modal de instrucciones para iOS Safari */}
      <PWAInstallModal
        isOpen={showIOSModal}
        onClose={() => setShowIOSModal(false)}
      />
    </div>
  );
}
