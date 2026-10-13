import { useState, ChangeEvent } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Award, 
  ShieldCheck, 
  UserCheck, 
  Search, 
  SlidersHorizontal, 
  X, 
  LogOut,
  WifiOff,
  RefreshCw,
  Building2,
  Globe,
  Link2,
  BarChart3,
  BookOpen
} from 'lucide-react';
import { useConnectivitySync } from '../storage/useConnectivitySync';
import { useTheme } from '../theme/ThemeProvider';
import type { TenantId } from '../theme/tokens';
import { useI18n } from '../i18n/useI18n';
import type { SupportedLocale } from '../../types/i18n';

export default function Navbar() {
  const { user, logout } = useAuth();
  const { tenant, tenantId, setTenantId, availableTenants } = useTheme();
  const { t, locale, changeLocale, supportedLocales, authority } = useI18n();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();
  const [showProfileMenu, setShowProfileMenu] = useState<boolean>(false);
  const { isOnline, isSyncing, pendingCount, syncPendingEvaluations } = useConnectivitySync();

  const searchQuery = searchParams.get('q') || '';

  const isAuthRoute = ['/login', '/register', '/auth/magic-login'].some(p => location.pathname.startsWith(p));

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    if (location.pathname !== '/') {
      navigate(`/?q=${encodeURIComponent(val)}`);
    } else {
      if (val) {
        setSearchParams({ q: val });
      } else {
        setSearchParams({});
      }
    }
  };

  const handleLogout = async () => {
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
    <header className="bg-white/85 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50 transition-colors">
      <div className="w-full max-w-[1680px] mx-auto px-4 sm:px-8 lg:px-12 h-16 flex items-center justify-between gap-4">
        
        {/* 1. Logo & Marca Ateneo+ */}
        <div className="flex items-center gap-3 shrink-0">
          <Link to="/" className="flex items-center gap-2.5 group">
            <img
              src="/ateneo.png"
              alt="Ateneo+ Logo"
              className="w-7 h-7 object-contain group-hover:scale-105 transition-transform"
            />
            <img
              src="/nombre.png"
              alt="Ateneo+"
              className="h-5 sm:h-6 w-auto object-contain group-hover:opacity-95 transition-opacity"
            />
          </Link>
        </div>

        {/* 2. Barra de Búsqueda (solo disponible para usuarios autenticados fuera del flujo de autenticación) */}
        {!isAuthRoute && user && (
          <div className="w-full max-w-2xl mx-auto hidden md:flex items-center">
            <div className="w-full bg-white/70 hover:bg-white/90 backdrop-blur-md focus-within:bg-white focus-within:shadow-md focus-within:shadow-indigo-500/5 focus-within:ring-2 focus-within:ring-blue-500/20 rounded-full px-4 py-2 transition-all flex items-center gap-3 border border-slate-200/60 focus-within:border-blue-400">
              <Search className="w-4 h-4 text-blue-600/70 shrink-0" />
              <input
                type="text"
                placeholder="Buscar en Ateneo: casos clínicos, síntomas, diagnósticos o GPC MSP..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full bg-transparent text-xs sm:text-sm text-[#1f1f1f] focus:outline-none placeholder:text-[#747775]"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchParams({})}
                  className="text-xs text-[#747775] hover:text-[#1f1f1f] p-1 rounded-full hover:bg-slate-200/60 transition-colors cursor-pointer"
                  title="Limpiar búsqueda"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
              <button
                title="Filtros de Búsqueda"
                onClick={() => navigate('/?filter=open')}
                className="p-1 text-[#747775] hover:text-[#1f1f1f] rounded-full hover:bg-slate-200/60 transition-colors cursor-pointer shrink-0"
              >
                <SlidersHorizontal className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* 3. Navegación, Conectividad y Perfil */}
        <div className="flex items-center gap-3 text-xs font-medium text-[#444746] shrink-0">
          {/* Indicador de Conectividad Clínica & Background Sync */}
          {!isOnline ? (
            <div 
              className="flex items-center gap-1.5 text-amber-700 font-medium px-2 py-1"
              title="Sin conexión de red hospitalaria. Modo local activo con buffer seguro."
            >
              <WifiOff className="w-3.5 h-3.5 text-amber-600 shrink-0" />
              <span className="hidden sm:inline">Modo Local</span>
            </div>
          ) : pendingCount > 0 ? (
            <button
              onClick={() => syncPendingEvaluations()}
              disabled={isSyncing}
              className="flex items-center gap-1.5 text-indigo-700 hover:text-indigo-900 transition-colors font-medium px-2 py-1 cursor-pointer"
              title="Sincronizar evaluaciones pendientes con el clúster central"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-indigo-600 ${isSyncing ? 'animate-spin' : ''}`} />
              <span>{pendingCount} pendiente{pendingCount > 1 ? 's' : ''}</span>
            </button>
          ) : null}

          {user ? (
            <>
              <Link
                to="/benchmark"
                title="Benchmark Científico"
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors ${
                  location.pathname === '/benchmark'
                    ? 'bg-sky-50 text-[#0b57d0] font-semibold'
                    : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100'
                }`}
              >
                <Award className="w-4 h-4 text-[#0b57d0]" />
                <span className="hidden sm:inline">Benchmark</span>
              </Link>

              {user.rol === 'administrador' && (
                <Link
                  to="/admin/users"
                  className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors ${
                    location.pathname.startsWith('/admin')
                      ? 'bg-purple-50 text-purple-700 font-semibold'
                      : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4 text-purple-600" />
                  <span>Admin</span>
                </Link>
              )}

              {(user.rol === 'docente' || user.rol === 'administrador') && (
                <Link
                  to="/teacher/cases"
                  className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full transition-colors ${
                    location.pathname.startsWith('/teacher')
                      ? 'bg-blue-50 text-blue-700 font-semibold'
                      : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100'
                  }`}
                >
                  <UserCheck className="w-4 h-4 text-blue-600" />
                  <span>Docente</span>
                </Link>
              )}

              {/* Avatar Circular con Iniciales */}
              <div className="relative">
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-xs flex items-center justify-center shadow-xs hover:ring-2 hover:ring-[#0b57d0]/40 transition-all cursor-pointer"
                  title={user.nombre}
                >
                  {getInitials(user.nombre)}
                </button>

                {showProfileMenu && (
                  <div className="absolute right-0 mt-2 w-64 bg-white rounded-[20px] shadow-lg border border-slate-200/80 p-4 z-50 animate-fadeIn">
                    <div className="text-center pb-3 border-b border-slate-100">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white font-semibold text-sm flex items-center justify-center mx-auto mb-2 shadow-xs">
                        {getInitials(user.nombre)}
                      </div>
                      <p className="font-semibold text-sm text-[#1f1f1f] truncate">{user.nombre}</p>
                      <p className="text-xs text-[#747775] truncate">{user.email || 'alumno@ateneo.edu.ec'}</p>
                      <div className="flex items-center justify-center gap-2 mt-1.5">
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-sky-50 text-[#0b57d0] uppercase">
                          {user.rol}
                        </span>
                        {(user.login_count !== undefined && user.login_count > 0) && (
                          <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-mono text-slate-500 bg-slate-100">
                            #{user.login_count}
                          </span>
                        )}
                      </div>
                      {user.last_login_at && (
                        <p className="text-[10px] text-slate-400 mt-2">
                          Último acceso: {new Date(user.last_login_at).toLocaleDateString('es-EC', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}
                        </p>
                      )}
                    </div>

                    {/* Sede Institucional (Multi-Tenancy con control RBAC) */}
                    {user.rol === 'administrador' ? (
                      <div className="py-3 border-b border-slate-100">
                        <label 
                          htmlFor="tenant-selector" 
                          className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5"
                        >
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>Sede Institucional</span>
                        </label>
                        <select
                          id="tenant-selector"
                          value={tenantId}
                          onChange={(e) => setTenantId(e.target.value as TenantId)}
                          className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                        >
                          {availableTenants.map((t) => (
                            <option key={t.id} value={t.id}>
                              {t.nombreInstitucion} ({t.siglas})
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <div className="py-3 border-b border-slate-100">
                        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                          <Building2 className="w-3.5 h-3.5 text-slate-400" />
                          <span>Sede Institucional</span>
                        </div>
                        <p className="text-xs font-medium text-slate-800 truncate" title={tenant.nombreInstitucion}>
                          {tenant.nombreInstitucion}
                        </p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">
                          {tenant.siglas} • {tenant.region}
                        </p>
                      </div>
                    )}

                    {/* Selector de Idioma */}
                    <div className="py-3 border-b border-slate-100">
                      <label 
                        htmlFor="locale-selector" 
                        className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5"
                      >
                        <Globe className="w-3.5 h-3.5 text-slate-400" />
                        <span>Idioma</span>
                      </label>
                      <select
                        id="locale-selector"
                        value={locale}
                        onChange={(e) => changeLocale(e.target.value as SupportedLocale)}
                        className="w-full text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                      >
                        {supportedLocales.map((loc) => (
                          <option key={loc.code} value={loc.code}>
                            {loc.label} ({loc.region})
                          </option>
                        ))}
                      </select>
                    </div>

                    {user.rol === 'alumno' && (
                      <div className="py-2 border-b border-slate-100 space-y-1">
                        <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 pb-0.5">
                          Mi Aprendizaje
                        </span>
                        <Link
                          to="/cases"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <BookOpen className="w-3.5 h-3.5 text-sky-600" />
                          <span>Casos Clínicos</span>
                        </Link>
                        <Link
                          to="/benchmark"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <Award className="w-3.5 h-3.5 text-[#0b57d0]" />
                          <span>Rendimiento y Benchmark</span>
                        </Link>
                      </div>
                    )}

                    {user.rol === 'administrador' && (
                      <div className="py-2 border-b border-slate-100 space-y-1">
                        <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 pb-0.5">
                          Administración
                        </span>
                        <Link
                          to="/admin/users"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <ShieldCheck className="w-3.5 h-3.5 text-purple-600" />
                          <span>Usuarios y Roles</span>
                        </Link>
                        <Link
                          to="/admin/magic-links"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <Link2 className="w-3.5 h-3.5 text-cyan-600" />
                          <span>Magic Links e Invitaciones</span>
                        </Link>
                      </div>
                    )}

                    {(user.rol === 'docente' || user.rol === 'administrador') && (
                      <div className="py-2 border-b border-slate-100 space-y-1">
                        <span className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 pb-0.5">
                          Docencia y Tutoría
                        </span>
                        <Link
                          to="/teacher/cases"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <UserCheck className="w-3.5 h-3.5 text-blue-600" />
                          <span>Casos y Salas Ateneo</span>
                        </Link>
                        <Link
                          to="/teacher/analytics"
                          onClick={() => setShowProfileMenu(false)}
                          className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                          <BarChart3 className="w-3.5 h-3.5 text-indigo-600" />
                          <span>Analítica de Cohorte</span>
                        </Link>
                      </div>
                    )}

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
            </>
          ) : location.pathname === '/login' ? (
            <Link
              to="/register"
              className="px-4 py-2 text-[#0b57d0] hover:bg-blue-50 rounded-full text-xs font-medium transition-colors"
            >
              Crear cuenta
            </Link>
          ) : (
            <Link
              to="/login"
              className="px-4 py-2 bg-[#0b57d0] hover:bg-blue-700 text-white rounded-full text-xs font-medium transition-colors"
            >
              Iniciar Sesión
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
