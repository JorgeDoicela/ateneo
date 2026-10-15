import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { ShieldCheck, AlertCircle, ArrowRight, Loader2, UserCheck, Stethoscope, GraduationCap } from 'lucide-react';
import useAuthStore from '../../../core/stores/useAuthStore';
import authApi from '../api/authApi';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';
import type { MagicLinkVerifyResult } from '../../../types';

/**
 * Página de Aterrizaje y Confirmación de Acceso por Magic Link (Ateneo+)
 * Muestra una tarjeta de bienvenida y confirmación interactiva antes de canjear el token,
 * evitando redirecciones invisibles y bloqueos de red en dispositivos móviles y de escritorio.
 * Cumple con el sistema de diseño clínico: Cero emojis, Material 3 Canvas (#f0f4f9).
 */
export const MagicLogin: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const token = searchParams.get('token') || '';

  const [verifying, setVerifying] = useState(true);
  const [linkData, setLinkData] = useState<MagicLinkVerifyResult | null>(null);
  const [requiresIdentity, setRequiresIdentity] = useState(false);
  const [email, setEmail] = useState('');
  const [nombre, setNombre] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!token) {
      setVerifying(false);
      setErrorMsg('No se proporcionó ningún token de acceso en el enlace.');
      return;
    }

    const checkLink = async () => {
      try {
        const data = await authApi.verifyMagicLink(token);
        setLinkData(data);
        setRequiresIdentity(data.requires_identity);
        if (data.email) {
          setEmail(data.email);
        }
        if (data.recipient_name) {
          setNombre(data.recipient_name);
        }
        setVerifying(false);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string }; status?: number }; message?: string };
        const detail = error.response?.data?.detail || error.message || '';
        setErrorMsg(detail || 'El enlace de acceso no es válido, ha expirado o ya fue utilizado.');
        setVerifying(false);
      }
    };

    checkLink();
  }, [token]);

  const handleConfirmEnter = async () => {
    setSubmitting(true);
    setErrorMsg(null);

    try {
      const result = await authApi.consumeMagicLink({
        token,
        email: email.trim() || undefined,
        nombre: nombre.trim() || undefined,
      });
      setAuth(result.user, result.access_token);
      const destination = result.target_path || (result.user.rol === 'docente' ? '/teacher/cases' : '/cases');
      navigate(destination, { replace: true });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setErrorMsg(
        error.response?.data?.detail || 'No se pudo canjear el enlace de acceso. Verifique sus credenciales.'
      );
      setSubmitting(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) {
      setErrorMsg('Por favor ingrese su correo electrónico institucional.');
      return;
    }
    await handleConfirmEnter();
  };

  const handleGuestQuickEnter = async () => {
    setSubmitting(true);
    setErrorMsg(null);
    const quickEmail = `invitado.${Date.now().toString(36)}@ateneo.edu.ec`;
    try {
      const result = await authApi.consumeMagicLink({
        token,
        email: quickEmail,
        nombre: nombre.trim() || 'Participante Invitado',
      });
      setAuth(result.user, result.access_token);
      navigate(result.target_path || '/cases', { replace: true });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setErrorMsg(error.response?.data?.detail || 'No se pudo canjear el enlace');
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full flex flex-col justify-center items-center py-6 selection:bg-cyan-100">
      <div className="w-full max-w-md bg-white rounded-[28px] shadow-sm p-8 sm:p-10 transition-all">
        {/* Encabezado Institucional */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="flex items-center gap-2.5 mb-3">
            <img
              src="/ateneo.png"
              alt="Ateneo+ Logo"
              className="w-8 h-8 object-contain"
            />
            <img
              src="/nombre.png"
              alt="Ateneo+"
              className="h-6 w-auto object-contain"
            />
          </div>
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            Invitación de Acceso Institucional
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Simulador Clínico
          </p>
        </div>

        {/* Estado 1: Verificando token */}
        {verifying && (
          <div className="flex flex-col items-center justify-center py-8 text-center space-y-4">
            <Loader2 className="w-10 h-10 text-cyan-600 animate-spin" />
            <div>
              <p className="text-slate-800 font-semibold text-base">
                Comprobando credenciales del enlace...
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Validando firma criptográfica y vigencia institucional.
              </p>
            </div>
          </div>
        )}

        {/* Estado 2: Error de token o enlace inválido */}
        {!verifying && errorMsg && !linkData && (
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

        {/* Estado 3: Enlace válido - Tarjeta de confirmación previa al ingreso */}
        {!verifying && linkData && !requiresIdentity && (
          <div className="space-y-6">
            <div className="p-5 bg-slate-50/80 border border-slate-100 rounded-2xl text-center space-y-2">
              <div className="flex justify-center">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-800">
                  {linkData.rol === 'docente' ? (
                    <>
                      <Stethoscope className="w-3.5 h-3.5 text-blue-600" />
                      <span>Docente</span>
                    </>
                  ) : linkData.rol === 'administrador' ? (
                    <>
                      <ShieldCheck className="w-3.5 h-3.5 text-cyan-600" />
                      <span>Administrador</span>
                    </>
                  ) : (
                    <>
                      <GraduationCap className="w-3.5 h-3.5 text-[#0b57d0]" />
                      <span>Estudiante</span>
                    </>
                  )}
                </span>
              </div>

              {linkData.recipient_name && (
                <p className="text-base font-semibold text-slate-800">
                  {linkData.recipient_name}
                </p>
              )}

              <p className="text-xs text-slate-500">
                Acceso preparado para iniciar la simulación.
              </p>
            </div>

            {errorMsg && (
              <div className="p-3 bg-rose-50 rounded-xl flex items-center gap-2 text-xs text-rose-700">
                <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <p className="text-xs text-slate-500 text-center leading-relaxed">
              Presione el botón para ingresar directamente a los casos de simulación clínica.
            </p>

            <button
              type="button"
              onClick={handleConfirmEnter}
              disabled={submitting}
              className="w-full py-4 px-6 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold text-sm transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Preparando entorno clínico...</span>
                </>
              ) : (
                <>
                  <span>Confirmar e Ingresar a Ateneo+</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="text-center pt-1">
              <Link
                to="/login"
                className="text-xs text-slate-500 hover:text-slate-800 transition-colors"
              >
                ¿Desea ingresar con otra cuenta? Ir al inicio de sesión
              </Link>
            </div>
          </div>
        )}

        {/* Estado 4: Enlace grupal de cohorte que requiere correo y nombre */}
        {!verifying && requiresIdentity && (
          <form onSubmit={handleManualSubmit} className="space-y-5">
            <div className="p-4 bg-cyan-50/70 rounded-2xl flex items-start gap-3 mb-2">
              <ShieldCheck className="w-5 h-5 text-cyan-700 shrink-0 mt-0.5" />
              <div>
                <h2 className="text-xs font-bold text-cyan-950 uppercase tracking-wider">
                  Invitación de Cohorte Médica
                </h2>
                <p className="text-xs text-cyan-850 mt-1 leading-relaxed text-slate-600">
                  Ha recibido una invitación grupal. Ingrese sus datos institucionales para
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

            <div className="space-y-2.5 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3.5 px-6 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-medium text-sm hover:from-cyan-700 hover:to-blue-700 transition-all shadow-sm flex items-center justify-center gap-2 disabled:opacity-60 cursor-pointer"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Validando acceso...</span>
                  </>
                ) : (
                  <>
                    <span>Confirmar e Ingresar a Ateneo+</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={handleGuestQuickEnter}
                disabled={submitting}
                className="w-full py-2.5 px-4 rounded-full bg-slate-100 hover:bg-slate-200/80 text-slate-700 text-xs font-semibold transition-colors flex items-center justify-center gap-2 cursor-pointer"
              >
                <span>Acceso Express en 1 Clic (Sin Correo)</span>
              </button>
            </div>

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
        Simulador Clínico &bull; GPC Ecuador
      </footer>
    </div>
  );
};

export default MagicLogin;
