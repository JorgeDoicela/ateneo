import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Building2, 
  Globe, 
  ShieldCheck, 
  Link2, 
  UserCheck, 
  BarChart3, 
  Award,
  LogOut 
} from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import { useTheme } from '../../theme/ThemeProvider';
import type { TenantId } from '../../theme/tokens';
import { useI18n } from '../../i18n/useI18n';
import type { SupportedLocale } from '../../../types/i18n';

/**
 * UserProfileDropdown — Menú compacto de identidad institucional y sesión
 * Diseñado bajo principios de UX limpia: sin redundancias de navegación,
 * cabecera horizontal y accesos administrativos estrictamente por rol.
 */
export default function UserProfileDropdown() {
  const { user, logout } = useAuth();
  const { tenant, tenantId, setTenantId, availableTenants } = useTheme();
  const { t, locale, changeLocale, supportedLocales } = useI18n();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  if (!user) return null;

  const handleLogout = async () => {
    setIsOpen(false);
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
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-xs flex items-center justify-center shadow-xs hover:ring-2 hover:ring-[#0b57d0]/40 transition-all cursor-pointer"
        title={user.nombre}
      >
        {getInitials(user.nombre)}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-[24px] shadow-xl border border-slate-200/80 p-4 z-50 animate-fadeIn">
          {/* 1. Cabecera de Identidad Compacta y Horizontal */}
          <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-xs flex items-center justify-center shrink-0 shadow-xs">
              {getInitials(user.nombre)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-semibold text-sm text-[#1f1f1f] truncate leading-tight">{user.nombre}</p>
              <p className="text-xs text-[#747775] truncate mt-0.5">{user.email || 'alumno@ateneo.edu.ec'}</p>
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

          {/* 5. Selector de Idioma Compacto e Inline */}
          <div className="flex items-center justify-between py-2 border-b border-slate-100 text-xs">
            <span className="flex items-center gap-1.5 text-slate-500 font-medium">
              <Globe className="w-3.5 h-3.5 text-slate-400" />
              Idioma
            </span>
            <select
              id="locale-selector"
              value={locale}
              onChange={(e) => changeLocale(e.target.value as SupportedLocale)}
              className="text-xs font-medium bg-transparent text-slate-700 focus:outline-none cursor-pointer pr-1"
            >
              {supportedLocales.map((locItem) => (
                <option key={locItem.code} value={locItem.code}>
                  {locItem.label}
                </option>
              ))}
            </select>
          </div>

          {/* 6. Botón Cerrar Sesión */}
          <div className="pt-2">
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-full text-xs font-medium text-rose-700 hover:bg-rose-50 transition-colors cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>{t('common.cerrarSesion')}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
