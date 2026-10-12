import { useState, FormEvent } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { AlertCircle, ChevronDown } from 'lucide-react';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';
import ClinicalButton from '../../../core/ui/ClinicalButton';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [step, setStep] = useState<number>(1); // 1: Email, 2: Password
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);

  const locationState = location.state as { from?: { pathname?: string } } | null;
  const from = locationState?.from?.pathname || '/';

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
      if (user.rol === 'administrador') {
        navigate('/admin');
      } else if (user.rol === 'docente') {
        navigate('/teacher');
      } else {
        navigate(from === '/login' ? '/' : from);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Contraseña incorrecta. Inténtalo de nuevo.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full min-h-[calc(100vh-160px)] flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-[1040px] bg-white rounded-[28px] p-8 sm:p-12 min-h-[420px] shadow-xs border-0 transition-all duration-300 flex flex-col justify-between">
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 items-stretch flex-1">
          {/* Columna Izquierda (5 cols): Marca, Identidad y Título Material 3 */}
          <div className="md:col-span-5 flex flex-col justify-between">
            <div>
              <img
                src="/ateneo.png"
                alt="Ateneo+"
                className="w-12 h-12 mb-4 object-contain"
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
                Simulador Clínico & Evaluación Médica con IA basada en Guías de Práctica Clínica del MSP Ecuador
              </p>
            </div>

            <div className="hidden md:flex items-center gap-4 text-xs text-[#747775] pt-6 border-t border-slate-100">
              <span>Normativa MSP 2026</span>
              <span>•</span>
              <span>Plataforma Académica</span>
            </div>
          </div>

          {/* Columna Derecha (7 cols): Formulario Flotante en 2 Pasos */}
          <div className="md:col-span-7 flex flex-col justify-between pt-4 md:pt-14">
            <div>
              {/* Notificación de Error */}
              {error && (
                <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200/80 rounded-[16px] flex items-start gap-2.5 text-xs text-rose-800 animate-fadeIn">
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
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

                  <div className="flex items-center justify-between pt-4">
                    <span className="text-xs text-[#747775]">
                      Dominio @ateneo.edu.ec
                    </span>
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
                  {/* Chip de cuenta seleccionada */}
                  <div
                    onClick={() => { setStep(1); setError(null); }}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-300 bg-[#f0f4f9] hover:bg-slate-100 cursor-pointer text-xs font-medium text-[#1f1f1f] transition-colors"
                  >
                    <span>{email}</span>
                    <ChevronDown className="w-3.5 h-3.5 text-[#747775]" />
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

                  <div className="flex items-center gap-2">
                    <input
                      id="show-pass"
                      type="checkbox"
                      checked={showPassword}
                      onChange={(e) => setShowPassword(e.target.checked)}
                      className="rounded border-slate-300 text-[#0b57d0] focus:ring-0 cursor-pointer"
                    />
                    <label htmlFor="show-pass" className="text-xs text-[#444746] cursor-pointer">
                      Mostrar contraseña
                    </label>
                  </div>

                  <div className="flex items-center justify-between pt-4">
                    <button
                      type="button"
                      onClick={() => { setStep(1); setError(null); }}
                      className="text-xs font-medium text-[#0b57d0] hover:underline cursor-pointer"
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
