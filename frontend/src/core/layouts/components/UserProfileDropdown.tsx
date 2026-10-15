import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Globe, 
  ShieldCheck, 
  Link2, 
  UserCheck, 
  BarChart3, 
  Award,
  LogOut,
  ChevronDown,
  Check,
  User,
  X,
  GraduationCap
} from 'lucide-react';
import ClinicalCareerModal from '../../../modules/gamification/components/ClinicalCareerModal';
import { useAuth } from '../../../context/AuthContext';
import { useTheme } from '../../theme/ThemeProvider';
import type { TenantId } from '../../theme/tokens';
import { useI18n } from '../../i18n/useI18n';
import type { SupportedLocale } from '../../../types/i18n';

export interface UserProfileDropdownProps {
  dropUp?: boolean;
  showLabel?: boolean;
}

/**
 * UserProfileDropdown — Modal institucional centrado de identidad y sesión
 * Renderizado vía React Portal hacia document.body con overlay backdrop-blur.
 */
export default function UserProfileDropdown({ showLabel = false }: UserProfileDropdownProps) {
  const { user, logout } = useAuth();
  const { tenant, tenantId, setTenantId, availableTenants } = useTheme();
  const { t, locale, changeLocale, supportedLocales } = useI18n();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [isLangOpen, setIsLangOpen] = useState<boolean>(false);
  const [showCareerModal, setShowCareerModal] = useState<boolean>(false);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
        setIsLangOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!user) return null;

  const handleLogout = async () => {
    setIsOpen(false);
    setIsLangOpen(false);
    await logout();
    navigate('/login');
  };

  const getInitials = (name?: string): string => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div>
      {showLabel ? (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="flex flex-col items-center justify-center py-1 px-1.5 text-slate-700 hover:text-[#0b57d0] active:scale-95 transition-all cursor-pointer group select-none"
          title={user.nombre}
        >
          <User className="w-5 h-5 text-slate-700 group-hover:text-[#0b57d0] transition-colors" />
          <span className="text-[11px] font-medium text-slate-600 group-hover:text-[#0b57d0] transition-colors mt-1 leading-none">
            Perfil
          </span>
        </button>
      ) : (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="w-8 h-8 sm:w-9 sm:h-9 shrink-0 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-xs flex items-center justify-center shadow-xs hover:ring-2 hover:ring-[#0b57d0]/40 transition-all cursor-pointer"
          title={user.nombre}
        >
          {getInitials(user.nombre)}
        </button>
      )}

      {isOpen && createPortal(
        <div 
          className="fixed inset-0 z-[100] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
          onClick={() => { setIsOpen(false); setIsLangOpen(false); }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="user-profile-title"
        >
          <div 
            className="bg-white rounded-[28px] shadow-2xl border border-slate-200/60 max-w-lg w-full p-6 sm:p-8 space-y-6 animate-scaleUp relative overflow-hidden"
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

            {/* Cabecera del Diálogo con X */}
            <div className="flex items-center justify-between border-b border-slate-100/90 pb-4 relative z-10">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-sm flex items-center justify-center shrink-0 shadow-xs">
                  {getInitials(user.nombre)}
                </div>
                <div className="min-w-0 flex-1">
                  <h3 id="user-profile-title" className="font-heading font-normal text-base text-slate-900 truncate leading-tight">
                    {user.nombre}
                  </h3>
                  <p className="text-xs text-slate-500 truncate mt-0.5">{user.email || 'alumno@ateneo.edu.ec'}</p>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-sky-50 text-[#0b57d0] uppercase tracking-wider">
                      {user.rol}
                    </span>
                    <span className="text-[10px] text-slate-400 truncate">
                      • {tenant.siglas || tenant.nombreInstitucion}
                    </span>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => { setIsOpen(false); setIsLangOpen(false); }}
                className="p-1.5 rounded-full hover:bg-slate-100 text-slate-400 hover:text-slate-700 cursor-pointer transition-colors"
                aria-label="Cerrar modal de perfil"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

          {/* 2. Selector de Sede Institucional (Restringido a Administradores) */}
          {user.rol === 'administrador' && (
            <div className="py-2.5 border-b border-slate-100">
              <label 
                htmlFor="tenant-selector" 
                className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1"
              >
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Cambiar Sede</span>
              </label>
              <select
                id="tenant-selector"
                value={tenantId}
                onChange={(e) => setTenantId(e.target.value as TenantId)}
                className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
              >
                {availableTenants.map((tenantItem) => (
                  <option key={tenantItem.id} value={tenantItem.id}>
                    {tenantItem.nombreInstitucion} ({tenantItem.siglas})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* 3. Accesos de Gestión para Administrador */}
          {user.rol === 'administrador' && (
            <div className="py-2 border-b border-slate-100 space-y-0.5">
              <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 pb-0.5">
                Administración
              </span>
              <Link
                to="/admin/users"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                <span>Usuarios y Roles</span>
              </Link>
              <Link
                to="/admin/magic-links"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <Link2 className="w-3.5 h-3.5 text-cyan-600" />
                <span>Magic Links e Invitaciones</span>
              </Link>
              <Link
                to="/benchmark"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <Award className="w-3.5 h-3.5 text-[#0b57d0]" />
                <span>Benchmark Científico del RAG</span>
              </Link>
            </div>
          )}

          {/* 4. Accesos de Gestión para Docente */}
          {(user.rol === 'docente' || user.rol === 'administrador') && (
            <div className="py-2 border-b border-slate-100 space-y-0.5">
              <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 pb-0.5">
                Docencia
              </span>
              <Link
                to="/teacher/cases"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                <span>Casos y Salas Ateneo</span>
              </Link>
              <Link
                to="/teacher/analytics"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
              >
                <BarChart3 className="w-3.5 h-3.5 text-indigo-600" />
                <span>Analítica de Cohorte</span>
              </Link>
            </div>
          )}

          {/* 5. Acceso a Carrera Formativa e Hitos Clínicos */}
          <div className="py-2 border-b border-slate-100">
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                setShowCareerModal(true);
              }}
              className="w-full flex items-center justify-between px-2.5 py-2 text-xs text-slate-700 hover:text-blue-600 hover:bg-slate-50 rounded-xl transition-colors cursor-pointer"
            >
              <span className="flex items-center gap-2 font-medium">
                <GraduationCap className="w-4 h-4 text-[#0b57d0]" />
                <span>Carrera Formativa e Hitos</span>
              </span>
              <span className="text-[10px] text-blue-600 font-semibold bg-blue-50 px-2 py-0.5 rounded-full">
                Ver Hitos
              </span>
            </button>
          </div>

          {/* 6. Selector de Idioma Customizado (Cero controles nativos del SO) */}
          <div className="py-2 border-b border-slate-100 text-xs space-y-1.5">
            <button
              type="button"
              onClick={() => setIsLangOpen(!isLangOpen)}
              className="w-full flex items-center justify-between py-1 text-slate-700 hover:text-blue-600 transition-colors cursor-pointer group"
            >
              <span className="flex items-center gap-1.5 text-slate-500 font-medium">
                <Globe className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-500 transition-colors" />
                Idioma
              </span>
              <span className="flex items-center gap-1 font-semibold text-slate-700 group-hover:text-blue-600">
                <span>{supportedLocales.find(l => l.code === locale)?.label || locale}</span>
                <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${isLangOpen ? 'rotate-180 text-blue-600' : ''}`} />
              </span>
            </button>

            {isLangOpen && (
              <div className="pt-1 pb-1 space-y-1 animate-fadeIn bg-slate-50/70 rounded-xl p-1.5 border border-slate-100">
                {supportedLocales.map((locItem) => (
                  <button
                    key={locItem.code}
                    type="button"
                    onClick={() => {
                      changeLocale(locItem.code as SupportedLocale);
                      setIsLangOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
                      locale === locItem.code
                        ? 'bg-blue-50 text-blue-700 font-semibold'
                        : 'text-slate-600 hover:bg-white hover:text-slate-900'
                    }`}
                  >
                    <span>{locItem.label}</span>
                    {locale === locItem.code && <Check className="w-3.5 h-3.5 text-blue-600" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* 6. Botón Cerrar Sesión */}
          <div className="pt-2">
            <button
              type="button"
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-full text-xs font-medium text-rose-700 hover:bg-rose-50 transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>{t('common.cerrarSesion')}</span>
            </button>
          </div>
        </div>
      </div>,
      document.body
    )}

    <ClinicalCareerModal
      isOpen={showCareerModal}
      onClose={() => setShowCareerModal(false)}
    />
  </div>
  );
}
