import React, { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, AlertCircle, ArrowRight, Loader2, Hospital } from 'lucide-react';
import useAuthStore from '../../../core/stores/useAuthStore';
import authApi from '../api/authApi';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';

/**
 * Página de Aterrizaje y Canje de Magic Links (Ateneo+)
 * Autentica e inicia sesión automáticamente o solicita identidad para enlaces grupales de cohorte.
 * Diseño clínico sobrio sin emojis con Material 3 Canvas (#f0f4f9).
 */
export const MagicLogin: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const token = searchParams.get('token') || '';
  const consumedRef = useRef(false);

  const [loading, setLoading] = useState(true);
  const [requiresIdentity, setRequiresIdentity] = useState(false);
  const [email, setEmail] = useState('');
  const [nombre, setNombre] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      setErrorMsg('No se proporcionó ningún token de acceso en el enlace.');
      return;
    }

    if (consumedRef.current) return;
    consumedRef.current = true;

    // Intento inicial de canje automático (para enlaces nominativos directos)
    const attemptAutoConsume = async () => {
      try {
        const result = await authApi.consumeMagicLink({ token });
        setAuth(result.user, result.access_token);
        navigate(result.target_path || '/cases', { replace: true });
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string }; status?: number }; message?: string };
        const detail = error.response?.data?.detail || error.message || '';
        
        // Si el backend indica que falta email (enlace grupal de cohorte), solicitamos identidad
        if (
          detail.toLowerCase().includes('requiere ingresar su correo') ||
          detail.toLowerCase().includes('email de participante') ||
          error.response?.status === 400
        ) {
          setRequiresIdentity(true);
          setLoading(false);
        } else {
          setErrorMsg(detail || 'El enlace de acceso no es válido, ha expirado o ya fue utilizado.');
          setLoading(false);
        }
      }
    };

    attemptAutoConsume();
  }, [token, navigate, setAuth]);

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrorMsg('Por favor ingrese su correo electrónico institucional.');
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    try {
      const result = await authApi.consumeMagicLink({
        token,
        email: email.trim(),
        nombre: nombre.trim() || undefined,
      });
      setAuth(result.user, result.access_token);
      navigate(result.target_path || '/cases', { replace: true });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setErrorMsg(
        error.response?.data?.detail || 'No se pudo canjear el enlace de acceso. Verifique sus datos.'
      );
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f0f4f9] flex flex-col justify-center items-center p-4 selection:bg-cyan-100">
      <div className="w-full max-w-md bg-white rounded-[28px] shadow-sm p-8 sm:p-10 transition-all">
        {/* Encabezado Institucional */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="flex items-center gap-2 mb-3">
            <Hospital className="w-8 h-8 text-cyan-600" />
            <span className="text-xl font-bold tracking-tight text-slate-800">
              Ateneo<span className="text-cyan-600">+</span>
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            Acceso Rápido Institucional
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Simulador Clínico y Evaluación Médica con IA
          </p>
        </div>

        {/* Estado 1: Cargando y canjeando automáticamente */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-8 text-center space-y-4">
            <Loader2 className="w-10 h-10 text-cyan-600 animate-spin" />
            <div>
              <p className="text-slate-800 font-semibold text-base">
                Verificando credenciales de acceso...
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Conectando con el servidor institucional y preparando el entorno clínico.
              </p>
            </div>
          </div>
        )}

        {/* Estado 2: Error de token o enlace inválido */}
        {!loading && errorMsg && !requiresIdentity && (
          <div className="space-y-6">
            <div className="p-4 bg-rose-50 rounded-2xl flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              <div>
                <h2 className="text-sm font-bold text-rose-900">Enlace no disponible</h2>
                <p className="text-xs text-rose-700 mt-1 leading-relaxed">{errorMsg}</p>
              </div>
            </div>

            <div className="text-center pt-2">
              <Link
                to="/login"
                className="inline-flex items-center justify-center gap-2 w-full py-3.5 px-6 rounded-full bg-slate-900 text-white font-medium text-sm hover:bg-slate-800 transition-colors shadow-sm"
              >
                <span>Ir al inicio de sesión regular</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        )}

        {/* Estado 3: Enlace grupal de cohorte que requiere correo y nombre */}
        {!loading && requiresIdentity && (
          <form onSubmit={handleManualSubmit} className="space-y-5">
            <div className="p-4 bg-cyan-50/70 rounded-2xl flex items-start gap-3 mb-2">
              <ShieldCheck className="w-5 h-5 text-cyan-700 shrink-0 mt-0.5" />
              <div>
                <h2 className="text-xs font-bold text-cyan-950 uppercase tracking-wider">
                  Invitación de Cohorte Médica
                </h2>
                <p className="text-xs text-cyan-850 mt-1 leading-relaxed text-slate-600">
                  Ha recibido una invitación grupal. Ingrese su información institucional para
                  vincular sus resoluciones clínicas y acceder a la plataforma.
                </p>
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-50 rounded-xl flex items-center gap-2 text-xs text-rose-700">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="space-y-4 pt-1">
              <FloatingLabelInput
                id="magic-email"
                type="email"
                label="Correo Institucional"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={submitting}
                placeholder="ejemplo@ateneo.edu.ec"
              />

              <FloatingLabelInput
                id="magic-nombre"
                type="text"
                label="Nombre y Apellido (Opcional)"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                disabled={submitting}
                placeholder="Dr(a). Juan Pérez"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-4 py-3.5 px-6 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-medium text-sm hover:from-cyan-700 hover:to-blue-700 transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validando acceso...</span>
                </>
              ) : (
                <>
                  <span>Ingresar a la Plataforma</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="text-center pt-2">
              <Link
                to="/login"
                className="text-xs text-slate-500 hover:text-slate-800 transition-colors"
              >
                ¿Ya dispone de una cuenta con contraseña? Iniciar sesión
              </Link>
            </div>
          </form>
        )}
      </div>

      {/* Pie de página institucional */}
      <footer className="mt-8 text-center text-xs text-slate-400">
        Sistema de Evaluación Médica y Razonamiento Clínico con IA &bull; MSP Ecuador
      </footer>
    </div>
  );
};

export default MagicLogin;
