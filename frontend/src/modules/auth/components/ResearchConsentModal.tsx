import { useState } from 'react';
import { createPortal } from 'react-dom';
import { FileText, CheckCircle2, Lock, AlertTriangle, LogOut } from 'lucide-react';
import { useAuthStore } from '../../../core/stores/useAuthStore';

interface ResearchConsentModalProps {
  onSuccess?: () => void;
}

export const ResearchConsentModal: React.FC<ResearchConsentModalProps> = ({ onSuccess }) => {
  const user = useAuthStore((state) => state.user);
  const acceptTermsAndUnlockSession = useAuthStore((state) => state.acceptTermsAndUnlockSession);
  const logout = useAuthStore((state) => state.logout);

  const [aceptaInvestigacion, setAceptaInvestigacion] = useState(false);
  const [aceptaDatos, setAceptaDatos] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const canProceed = aceptaInvestigacion && aceptaDatos;

  const handleConfirm = async () => {
    if (!canProceed || isSubmitting) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await acceptTermsAndUnlockSession('v1.0-investigacion-2026');
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: unknown) {
      console.error('Error al registrar aceptación de términos:', err);
      setErrorMessage('No fue posible registrar su consentimiento. Intente nuevamente o cierre sesión.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    await logout();
  };

  const modalContent = (
    <div 
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="consent-modal-title"
    >
      <div className="relative w-full max-w-2xl bg-white rounded-[28px] shadow-2xl p-6 sm:p-8 my-auto text-slate-800 animate-scaleUp">
        {/* Encabezado con Imagotipo Oficial */}
        <div className="flex items-start gap-4 mb-5 pb-5 border-b border-slate-100">
          <img 
            src="/ateneo.png" 
            alt="Ateneo+" 
            className="w-10 h-10 object-contain shrink-0 select-none" 
          />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2 mb-0.5">
              <span className="font-heading font-black text-sm tracking-tight text-slate-900">
                ATENEO<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600">+</span>
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-[11px] font-semibold text-slate-500">Protocolo de Investigación</span>
            </div>
            <h2 id="consent-modal-title" className="text-xl font-bold text-slate-900 font-heading tracking-tight">
              Consentimiento Informado y Descargo Legal
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Prueba Piloto Académica y Tratamiento de Datos Personales conforme a la LOPDP
            </p>
          </div>
        </div>

        {/* Advertencia Principal en Tipografía Plana */}
        <div className="mb-5 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-700">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span className="uppercase tracking-wider text-[11px]">Versión Experimental y Prototipo Académico en Desarrollo Activo</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Ateneo+ es una plataforma de software desarrollada en el marco de una investigación médica real y rigurosa sobre educación clínica asistida por Inteligencia Artificial y RAG. Actualmente se encuentra en desarrollo activo y prueba piloto de validación formativa. Las limitaciones vigentes de uso obedecen a medidas de protección legal durante esta etapa de experimentación; al concluir con éxito la validación metodológica, se prevé el lanzamiento de una versión oficial. Durante esta fase temporal, los modelos están destinados exclusivamente a la simulación formativa y no constituyen decisiones diagnósticas ni recomendaciones terapéuticas vinculantes en pacientes reales.
          </p>
        </div>

        {/* Cláusulas Informativas Completas (Sin Scroll Anidado) */}
        <div className="space-y-3 mb-6 text-xs text-slate-600 leading-relaxed divide-y divide-slate-100">
          <div className="pt-2 first:pt-0">
            <h3 className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
              <FileText className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              1. Finalidad Exclusivamente Educativa y de Investigación
            </h3>
            <p>
              El acceso forma parte de un estudio experimental y validación de tecnologías de simulación clínica interactiva con base en las Guías de Práctica Clínica (GPC). Todos los casos clínicos presentados son ficticios, diseñados para entrenamiento y evaluación formativa del razonamiento clínico mientras avanza la investigación.
            </p>
          </div>

          <div className="pt-2">
            <h3 className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
              <Lock className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              2. Protección y Tratamiento de Datos Personales (LOPDP)
            </h3>
            <p>
              De conformidad con la Ley Orgánica de Protección de Datos Personales (LOPDP) y estándares bioéticos, el usuario autoriza el tratamiento, registro y análisis anonimizado de sus interacciones (respuestas diagnósticas, justificaciones, transcripciones de voz y métricas formativas) con fines estrictamente científicos, estadísticos y de mejora de modelos pedagógicos rumbo a futuras versiones oficiales.
            </p>
          </div>

          <div className="pt-2">
            <h3 className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-slate-500 shrink-0" />
              3. Participación Voluntaria en Prueba Piloto
            </h3>
            <p>
              El usuario reconoce que su acceso constituye una prueba piloto supervisada institucionalmente dentro de un proyecto de investigación en desarrollo activo. Puede revocar su participación o solicitar la anonimización total de sus registros académicos coordinando con la administración del sistema.
            </p>
          </div>
        </div>

        {/* Mensaje de Error si aplica */}
        {errorMessage && (
          <p className="mb-4 text-xs font-medium text-rose-600">
            {errorMessage}
          </p>
        )}

        {/* Casillas Obligatorias de Aceptación Planas */}
        <div className="space-y-2 mb-6 pt-3 border-t border-slate-100">
          <label className="flex items-start gap-3 p-2.5 rounded-2xl hover:bg-slate-50 transition-colors cursor-pointer select-none">
            <input
              type="checkbox"
              checked={aceptaInvestigacion}
              onChange={(e) => setAceptaInvestigacion(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 cursor-pointer"
            />
            <span className="text-xs text-slate-700 leading-relaxed">
              He leído y comprendo que Ateneo+ es una <strong>investigación científica real en desarrollo activo</strong>, y que por protección legal institucional su uso es de momento formativo y experimental, sin aplicación en pacientes reales hasta el eventual lanzamiento de una versión oficial.
            </span>
          </label>

          <label className="flex items-start gap-3 p-2.5 rounded-2xl hover:bg-slate-50 transition-colors cursor-pointer select-none">
            <input
              type="checkbox"
              checked={aceptaDatos}
              onChange={(e) => setAceptaDatos(e.target.checked)}
              className="mt-0.5 h-4 w-4 rounded border-slate-300 text-sky-600 focus:ring-sky-500 cursor-pointer"
            />
            <span className="text-xs text-slate-700 leading-relaxed">
              Autorizo el <strong>tratamiento y análisis de datos de simulación</strong> con fines de investigación científica, validación metodológica y evaluación de calidad pedagógica conforme a la normativa LOPDP.
            </span>
          </label>
        </div>

        {/* Acciones */}
        <div className="flex flex-col-reverse sm:flex-row items-center justify-between gap-3 pt-2">
          <button
            type="button"
            onClick={handleReject}
            disabled={isSubmitting}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            Rechazar y Cerrar Sesión
          </button>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={!canProceed || isSubmitting}
            className={`w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-2.5 rounded-full text-xs font-medium transition-all ${
              canProceed && !isSubmitting
                ? 'bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 text-white shadow-md shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 active:scale-[0.99] cursor-pointer'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? (
              <span className="inline-flex items-center gap-2">
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Registrando Consentimiento...
              </span>
            ) : (
              'Confirmar Consentimiento e Ingresar'
            )}
          </button>
        </div>

        {/* Usuario conectado info discreta */}
        {user && (
          <p className="text-[11px] text-center text-slate-400 mt-4">
            Sesión iniciada como: <span className="font-semibold text-slate-600">{user.nombre}</span> ({user.email})
          </p>
        )}
      </div>
    </div>
  );

  return typeof document !== 'undefined' ? createPortal(modalContent, document.body) : modalContent;
};

export default ResearchConsentModal;
