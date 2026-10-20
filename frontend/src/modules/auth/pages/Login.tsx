import { useState, useEffect, FormEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { AlertCircle, ChevronDown } from 'lucide-react';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';
import ClinicalButton from '../../../core/ui/ClinicalButton';

/**
 * Validador y saneador de ruta de redirección interna (CWE-601 Open Redirect Protection).
 * Soporta cadenas o instancias Location con query params y hashes.
 */
function sanitizeRedirectUrl(target: unknown): string | null {
  if (!target) return null;
  let path = '';
  if (typeof target === 'string') {
    path = target.trim();
  } else if (typeof target === 'object' && target !== null && 'pathname' in target) {
    const loc = target as { pathname?: string; search?: string; hash?: string };
    path = `${loc.pathname || ''}${loc.search || ''}${loc.hash || ''}`.trim();
  }

  // Debe ser una ruta interna relativa estricta, sin prefijos de protocolo ni barra doble
  if (path.startsWith('/') && !path.startsWith('//') && !path.startsWith('/login') && !path.startsWith('/register')) {
    return path;
  }
  return null;
}

export default function Login() {
  const { login, user: currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState<number>(1); // 1: Email, 2: Password
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const locationState = location.state as { from?: unknown } | null;
  const redirectTarget = sanitizeRedirectUrl(locationState?.from);

  // Redirección inmediata si ya existe una sesión autenticada activa
  useEffect(() => {
    if (currentUser && !authLoading) {
      if (redirectTarget && redirectTarget !== '/') {
        navigate(redirectTarget, { replace: true });
      } else if (currentUser.rol === 'administrador') {
        navigate('/admin', { replace: true });
      } else if (currentUser.rol === 'docente') {
        navigate('/teacher', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    }
  }, [currentUser, authLoading, redirectTarget, navigate]);

  const handleNextStep = (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !email.trim()) {
      setError('Ingresa un correo electrónico o institucional');
      return;
    }
    setStep(2);
  };

  const handleFinalSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!password) {
      setError('Ingresa tu contraseña');
      return;
    }
    setSubmitting(true);

    try {
      const user = await login(email, password);
      // Si el usuario intentó acceder a un recurso específico (ej. un caso clínico),
      // redirigirlo directamente a su destino solicitado
      if (redirectTarget && redirectTarget !== '/') {
        navigate(redirectTarget);
      } else if (user.rol === 'administrador') {
        navigate('/admin');
      } else if (user.rol === 'docente') {
        navigate('/teacher');
      } else {
        navigate('/');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Contraseña incorrecta. Inténtalo de nuevo.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center relative">
      {/* Halos de Luz Ambiental para Refracción de Cristal en Auth */}
      <div 
        className="pointer-events-none absolute -top-24 -left-20 w-80 h-80 bg-gradient-to-br from-cyan-400/20 via-blue-500/15 to-transparent rounded-full blur-3xl"
        aria-hidden="true"
      />
      <div 
        className="pointer-events-none absolute -bottom-20 -right-16 w-88 h-88 bg-gradient-to-tl from-indigo-500/15 via-violet-500/10 to-transparent rounded-full blur-3xl"
        aria-hidden="true"
      />

      <div className="w-full max-w-[1040px] bg-white rounded-[28px] p-8 sm:p-12 min-h-[420px] shadow-xs border border-slate-200/60 transition-all duration-300 flex flex-col justify-between relative z-10">
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 items-stretch flex-1">
          {/* Columna Izquierda (5 cols): Marca, Identidad y Título Material 3 */}
          <div className="md:col-span-5 flex flex-col justify-between">
            <div>
              <img
                src="/ateneo.png"
                alt="Ateneo+"
                className="w-12 h-12 mb-4 object-contain select-none"
              />
              <div className="flex items-center gap-1.5 mb-2">
                <span className="font-heading font-black text-2xl tracking-tight text-slate-900">
                  ATENEO<span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600">+</span>
                </span>
              </div>
              <h1 className="text-[28px] sm:text-[34px] font-normal text-[#1f1f1f] leading-[1.25] tracking-tight font-heading">
                Accede a tu cuenta
              </h1>
              <p className="text-sm font-normal text-[#444746] mt-2 leading-relaxed">
                Simulador Clínico basado en Guías de Práctica Clínica (GPC Ecuador)
              </p>
            </div>

            <div className="pt-6 border-t border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs">
                <span className="font-bold text-[10px] text-amber-700 uppercase tracking-wider">
                  Fase Experimental
                </span>
                <span className="text-slate-300">•</span>
                <span className="text-[11px] text-slate-500 font-medium">Investigación en Desarrollo Activo</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                Plataforma en protocolo de investigación científica y validación formativa. De momento restringida a simulación médica por protección legal, con proyección a una versión oficial.
              </p>
            </div>
          </div>

          {/* Columna Derecha (7 cols): Formulario Flotante en 2 Pasos */}
          <div className="md:col-span-7 flex flex-col justify-between pt-4 md:pt-16">
            <div>
              {/* Notificación de Error */}
              {error && (
                <div className={`mb-6 p-3.5 rounded-[16px] flex items-start gap-2.5 text-xs animate-fadeIn ${
                  error.toLowerCase().includes('bloqueada')
                    ? 'bg-amber-50/90 border border-amber-200 text-amber-900'
                    : 'bg-rose-50/90 border border-rose-200/80 text-rose-800'
                }`}>
                  <AlertCircle className={`w-4 h-4 shrink-0 mt-0.5 ${
                    error.toLowerCase().includes('bloqueada') ? 'text-amber-600' : 'text-rose-600'
                  }`} />
                  <span className="leading-snug">{error}</span>
                </div>
              )}

              {/* Paso 1: Identificación de Correo */}
              {step === 1 && (
                <form onSubmit={handleNextStep} className="space-y-6">
                  <FloatingLabelInput
                    id="email"
                    label="Correo electrónico"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoFocus
                  />

                  <div className="flex items-center justify-end gap-3 pt-4">
                    <Link
                      to="/register"
                      className="px-4 py-2.5 text-xs sm:text-sm font-medium text-slate-700 hover:text-blue-700 bg-white/70 hover:bg-gradient-to-r hover:from-cyan-50/50 hover:via-blue-50/40 hover:to-indigo-50/50 border border-slate-200/60 hover:border-blue-200 rounded-full transition-all cursor-pointer shadow-2xs"
                    >
                      Crear cuenta
                    </Link>
                    <ClinicalButton
                      type="submit"
                      variant="primary"
                      size="md"
                    >
                      Siguiente
                    </ClinicalButton>
                  </div>
                </form>
              )}

              {/* Paso 2: Contraseña de Acceso */}
              {step === 2 && (
                <form onSubmit={handleFinalSubmit} className="space-y-6">
                  {/* Chip de cuenta seleccionada en cristal líquido */}
                  <div
                    onClick={() => { setStep(1); setError(null); }}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-200/80 bg-white/80 hover:bg-white hover:border-blue-200 shadow-2xs cursor-pointer text-xs font-medium text-slate-800 transition-all group"
                  >
                    <span className="text-slate-700 group-hover:text-blue-700 transition-colors">{email}</span>
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 transition-colors" />
                  </div>

                  <FloatingLabelInput
                    id="password"
                    label="Contraseña de acceso"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoFocus
                  />

                  <div className="flex items-center gap-2.5">
                    <input
                      id="show-pass"
                      type="checkbox"
                      checked={showPassword}
                      onChange={(e) => setShowPassword(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-0 cursor-pointer accent-blue-600"
                    />
                    <label htmlFor="show-pass" className="text-xs text-slate-600 cursor-pointer select-none">
                      Mostrar contraseña
                    </label>
                  </div>

                  <div className="flex items-center justify-end gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => { setStep(1); setError(null); }}
                      className="px-4 py-2.5 text-xs sm:text-sm font-medium text-slate-700 hover:text-slate-900 bg-white/70 hover:bg-slate-100/80 border border-slate-200/60 rounded-full transition-all cursor-pointer shadow-2xs"
                    >
                      Volver
                    </button>
                    <ClinicalButton
                      type="submit"
                      variant="primary"
                      size="md"
                      loading={submitting}
                    >
                      Ingresar
                    </ClinicalButton>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
