import { useState, useMemo, useEffect, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AlertCircle, CheckCircle2, Building2 } from 'lucide-react';
import FloatingLabelInput from '../../../core/ui/FloatingLabelInput';
import ClinicalButton from '../../../core/ui/ClinicalButton';
import { useAuth } from '../../../context/AuthContext';
import { authApi } from '../api/authApi';
import type { RegisterRequest } from '../../../types';

interface DetectedTenant {
  codigo: string;
  nombre: string;
  siglas: string;
}

const INSTITUTIONAL_DOMAINS: Record<string, DetectedTenant> = {
  'uce.edu.ec': {
    codigo: 'uce',
    nombre: 'Universidad Central del Ecuador (Facultad de Ciencias Médicas)',
    siglas: 'UCE'
  },
  'usfq.edu.ec': {
    codigo: 'usfq',
    nombre: 'Universidad San Francisco de Quito (Colegio de Ciencias de la Salud)',
    siglas: 'USFQ'
  },
  'ateneo.edu.ec': {
    codigo: 'ateneo_central',
    nombre: 'Ateneo+ Sede Central (GPC Ecuador)',
    siglas: 'ATENEO+'
  }
};

export default function Register() {
  const { user: currentUser, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  const [nombre, setNombre] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [registeredSuccess, setRegisteredSuccess] = useState<string | null>(null);

  // Redirección si ya existe una sesión autenticada activa
  useEffect(() => {
    if (currentUser && !authLoading) {
      if (currentUser.rol === 'administrador') {
        navigate('/admin', { replace: true });
      } else if (currentUser.rol === 'docente') {
        navigate('/teacher', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    }
  }, [currentUser, authLoading, navigate]);

  // Detección reactiva de sede institucional por dominio de correo
  const detectedTenant = useMemo<DetectedTenant | null>(() => {
    if (!email || !email.includes('@')) return null;
    const parts = email.trim().toLowerCase().split('@');
    if (parts.length < 2) return null;
    const domain = parts[1];
    return INSTITUTIONAL_DOMAINS[domain] || null;
  }, [email]);

  // Validación de robustez de contraseña conforme al estándar médico
  const passwordCriteria = useMemo(() => {
    const hasMinLength = password.length >= 8;
    const hasDigit = /\d/.test(password);
    const hasUpperOrSymbol = /[A-Z]/.test(password) || /[^a-zA-Z0-9]/.test(password);
    return {
      hasMinLength,
      hasDigit,
      hasUpperOrSymbol,
      isValid: hasMinLength && hasDigit && hasUpperOrSymbol
    };
  }, [password]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!nombre.trim() || nombre.trim().length < 3) {
      setError('Por favor, ingresa tu nombre y apellido completo (mínimo 3 caracteres).');
      return;
    }

    if (!email.trim() || !email.includes('@')) {
      setError('Por favor, ingresa una dirección de correo institucional válida.');
      return;
    }

    if (!detectedTenant) {
      setError('El dominio ingresado no está habilitado. Utiliza tu correo institucional (@uce.edu.ec, @usfq.edu.ec o @ateneo.edu.ec).');
      return;
    }

    if (!passwordCriteria.isValid) {
      setError('La contraseña debe tener al menos 8 caracteres, incluir al menos un número y una mayúscula o símbolo.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Las contraseñas ingresadas no coinciden.');
      return;
    }

    setSubmitting(true);

    try {
      const payload: RegisterRequest = {
        nombre: nombre.trim(),
        email: email.trim().toLowerCase(),
        password,
        rol: 'alumno'
      };

      const res = await authApi.register(payload);
      setRegisteredSuccess(res.mensaje || 'Cuenta institucional creada exitosamente.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'No fue posible completar el registro. Inténtalo de nuevo.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center justify-center">
      <div className="w-full max-w-[1040px] bg-white rounded-[28px] p-8 sm:p-12 min-h-[460px] shadow-xs border-0 transition-all duration-300 flex flex-col justify-between">
        
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 md:gap-12 items-stretch flex-1">
          {/* Columna Izquierda (5 cols): Marca Institucional y Contexto Académico */}
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
                Crea tu cuenta institucional
              </h1>
              <p className="text-sm font-normal text-[#444746] mt-2 leading-relaxed">
                Plataforma de evaluación clínica y simulación formativa basada en las Guías de Práctica Clínica del Ministerio de Salud Pública de Ecuador.
              </p>
            </div>

            <div className="hidden md:flex items-center gap-4 text-xs text-[#747775] pt-6 border-t border-slate-100">
              <span>Normativa GPC Ecuador</span>
              <span>•</span>
              <span>Registro Institucional</span>
            </div>
          </div>

          {/* Columna Derecha (7 cols): Formulario Flotante Material 3 */}
          <div className="md:col-span-7 flex flex-col justify-between pt-2 md:pt-6">
            <div>
              {/* Notificación de Éxito */}
              {registeredSuccess ? (
                <div className="space-y-6 animate-fadeIn py-4">
                  <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-[20px] flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-sm font-semibold text-emerald-900">Registro completado</h3>
                      <p className="text-xs text-emerald-800 mt-1 leading-relaxed">
                        {registeredSuccess}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-end pt-4">
                    <ClinicalButton
                      type="button"
                      variant="primary"
                      size="md"
                      onClick={() => navigate('/login')}
                    >
                      Iniciar Sesión
                    </ClinicalButton>
                  </div>
                </div>
              ) : (
                <>
                  {/* Notificación de Error */}
                  {error && (
                    <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200/80 rounded-[16px] flex items-start gap-2.5 text-xs text-rose-800 animate-fadeIn">
                      <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                      <span className="leading-snug">{error}</span>
                    </div>
                  )}

                  {/* Píldora de Sede Universitaria Detectada */}
                  {detectedTenant ? (
                    <div className="mb-5 px-3.5 py-2.5 bg-sky-50/80 border border-sky-200/80 rounded-[16px] flex items-center gap-2.5 text-xs text-sky-900 animate-fadeIn">
                      <Building2 className="w-4 h-4 text-[#0b57d0] shrink-0" />
                      <span className="font-medium truncate">{detectedTenant.nombre}</span>
                      <span className="ml-auto text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-white text-[#0b57d0] border border-sky-200 shadow-2xs">
                        {detectedTenant.siglas}
                      </span>
                    </div>
                  ) : (
                    <div className="mb-5 px-3 py-2 bg-slate-50 border border-slate-200/60 rounded-[14px] text-[11px] text-slate-500 flex items-center gap-2">
                      <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>Ingresa tu correo institucional para asociar automáticamente tu universidad u hospital.</span>
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <FloatingLabelInput
                      id="register-nombre"
                      label="Nombres y apellidos completos"
                      type="text"
                      value={nombre}
                      onChange={(e) => setNombre(e.target.value)}
                      required
                      autoFocus
                    />

                    <FloatingLabelInput
                      id="register-email"
                      label="Correo electrónico institucional"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />

                    <FloatingLabelInput
                      id="register-password"
                      label="Contraseña"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />

                    <FloatingLabelInput
                      id="register-confirm-password"
                      label="Confirmar contraseña"
                      type={showPassword ? 'text' : 'password'}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      required
                    />

                    <div className="flex items-center justify-between text-xs pt-1">
                      <div className="flex items-center gap-2">
                        <input
                          id="show-pass-register"
                          type="checkbox"
                          checked={showPassword}
                          onChange={(e) => setShowPassword(e.target.checked)}
                          className="rounded border-slate-300 text-[#0b57d0] focus:ring-0 cursor-pointer"
                        />
                        <label htmlFor="show-pass-register" className="text-xs text-[#444746] cursor-pointer">
                          Mostrar contraseñas
                        </label>
                      </div>

                      {/* Micro-indicador de robustez */}
                      {password && (
                        <div className="flex items-center gap-1.5 text-[11px]">
                          <span className={passwordCriteria.isValid ? 'text-emerald-600 font-medium' : 'text-slate-400'}>
                            {passwordCriteria.isValid ? 'Contraseña robusta' : 'Mínimo 8 caracteres, números y mayúsculas'}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-4">
                      <Link
                        to="/login"
                        className="text-xs font-medium text-[#0b57d0] hover:underline cursor-pointer"
                      >
                        ¿Ya tienes cuenta? Iniciar sesión
                      </Link>
                      <ClinicalButton
                        type="submit"
                        variant="primary"
                        size="md"
                        loading={submitting}
                      >
                        Registrarse
                      </ClinicalButton>
                    </div>
                  </form>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
