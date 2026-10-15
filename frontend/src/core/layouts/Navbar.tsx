import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Award, 
  ShieldCheck, 
  UserCheck, 
  TrendingUp, 
  Users, 
  BookOpen, 
  Search, 
  ArrowLeft 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import GlobalSearchBar from './components/GlobalSearchBar';
import ConnectivityBadge from './components/ConnectivityBadge';
import UserProfileDropdown from './components/UserProfileDropdown';
import NotificationsDropdown from './components/NotificationsDropdown';
import MobileBottomNav from './components/MobileBottomNav';
import JoinRoomModal from '../../modules/collaboration/components/JoinRoomModal';

/**
 * Navbar — Cabecera principal desacoplada y fijada superior (Liquid Glassmorphism)
 * Orquestador modular de alta cohesión con transformación in-place para búsqueda móvil:
 * - Brand Logo & Slogan
 * - GlobalSearchBar (Spotlight Clínico Inteligente)
 * - ConnectivityBadge (Buffer offline y sincronización hospitalaria)
 * - Enlaces RBAC (Benchmark, Desempeño, Admin, Docente)
 * - UserProfileDropdown (Menú de identidad institucional y sesión)
 * - MobileBottomNav (Barra de navegación inferior móvil exclusiva del catálogo)
 */
export default function Navbar() {
  const { user } = useAuth();
  const location = useLocation();
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [showMobileSearch, setShowMobileSearch] = useState(false);
  const isAnalyticsView = location.pathname === '/analytics' || location.pathname === '/performance';
  const isCatalogRoute = location.pathname === '/' || location.pathname === '/cases';

  return (
    <header className="bg-white/85 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50 transition-colors w-full">
      <div className="w-full max-w-[1680px] mx-auto px-3 sm:px-8 lg:px-12 h-16 flex items-center justify-between gap-2 sm:gap-4 relative">
        
        {/* Transformación Profesional In-Place de la Cabecera en Móvil (Liquid Glassmorphism) */}
        {showMobileSearch && user ? (
          <div className="md:hidden w-full flex items-center gap-2.5 animate-glass-morph py-1.5 relative">
            <button
              type="button"
              onClick={() => setShowMobileSearch(false)}
              className="p-2 -ml-0.5 rounded-full bg-white/75 backdrop-blur-md border border-white/90 shadow-[0_2px_8px_rgba(0,0,0,0.04),inset_0_1px_1px_rgba(255,255,255,0.9)] text-[#0b57d0] hover:bg-white active:scale-90 transition-all cursor-pointer shrink-0"
              title="Volver"
            >
              <ArrowLeft className="w-4 h-4 text-[#0b57d0]" />
            </button>
            <div className="flex-1 min-w-0">
              <GlobalSearchBar isMobile onClose={() => setShowMobileSearch(false)} />
            </div>
          </div>
        ) : (
          <>
            {/* 1. Logo & Identidad de Marca Ateneo+ */}
            <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
              <Link to="/" className="flex items-center gap-2 sm:gap-2.5 select-none" title="Ateneo+">
                <img
                  src="/ateneo.png"
                  alt="Ateneo+ Logo"
                  style={{ width: '26px', height: '26px' }}
                  className="w-6 h-6 sm:w-7 sm:h-7 object-contain shrink-0"
                />
                <img
                  src="/nombre.png"
                  alt="Ateneo+"
                  style={{ height: '18px', maxHeight: '18px', width: 'auto', display: 'block' }}
                  className="h-[18px] max-h-[18px] w-auto object-contain shrink-0 hover:opacity-90 transition-opacity"
                />
              </Link>
            </div>

            {/* 2. Barra de Búsqueda Global Desacoplada (Escritorio) */}
            <GlobalSearchBar />

            {/* 3. Navegación, Conectividad Clínica y Perfil */}
            <div className="flex items-center gap-1.5 sm:gap-3 text-xs font-medium text-[#444746] shrink-0">
              {/* Botón de Búsqueda Móvil en Cabecera (Exclusivo del catálogo de casos clínicos) */}
              {user && isCatalogRoute && (
                <button
                  type="button"
                  onClick={() => setShowMobileSearch(true)}
                  title="Buscar casos clínicos"
                  className="md:hidden p-2 rounded-full text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  <Search className="w-5 h-5 text-[#0b57d0]" strokeWidth={2.2} />
                </button>
              )}

              {/* Indicador de Conectividad & Sincronización Offline */}
              <ConnectivityBadge />

              {user ? (
                <>
                  {/* Enlace Dinámico Desempeño / Catálogo (Exclusivo de escritorio) */}
                  <Link
                    to={isAnalyticsView ? '/cases' : '/analytics'}
                    title={isAnalyticsView ? 'Volver al Catálogo de Casos' : 'Mi Desempeño y Tendencias Clínicas'}
                    className={`hidden md:flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-full text-xs font-medium transition-all duration-200 select-none ${
                      isAnalyticsView
                        ? 'bg-gradient-to-r from-cyan-100/80 via-blue-100/70 to-indigo-100/80 text-[#0b57d0] font-semibold border border-blue-300/80 shadow-xs'
                        : 'bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm'
                    }`}
                  >
                    {isAnalyticsView ? (
                      <>
                        <BookOpen className="w-4 h-4 text-[#0b57d0]" />
                        <span className="hidden sm:inline">Catálogo</span>
                      </>
                    ) : (
                      <>
                        <TrendingUp className="w-4 h-4 text-[#0b57d0]" />
                        <span className="hidden sm:inline">Desempeño</span>
                      </>
                    )}
                  </Link>

                  {/* Botón Unirse a Sala Colaborativa (Exclusivo de escritorio) */}
                  <button
                    type="button"
                    onClick={() => setShowJoinModal(true)}
                    title="Unirse a Sala de Ateneo"
                    className="hidden md:flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-full text-xs font-medium transition-all duration-200 bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm cursor-pointer select-none"
                  >
                    <Users className="w-4 h-4 text-[#0b57d0]" />
                    <span className="hidden md:inline">Unirse a Sala</span>
                  </button>

                  {/* Enlace Benchmark (Restringido a Administradores) */}
                  {user.rol === 'administrador' && (
                    <Link
                      to="/benchmark"
                      title="Benchmark Científico"
                      className={`flex items-center gap-1.5 p-2 sm:px-3 sm:py-1.5 rounded-full text-xs font-medium transition-all duration-200 select-none ${
                        location.pathname === '/benchmark'
                          ? 'bg-gradient-to-r from-cyan-100/80 via-blue-100/70 to-indigo-100/80 text-[#0b57d0] font-semibold border border-blue-300/80 shadow-xs'
                          : 'bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-[#0b57d0] border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm'
                      }`}
                    >
                      <Award className="w-4 h-4 text-[#0b57d0]" />
                      <span className="hidden lg:inline">Benchmark</span>
                    </Link>
                  )}

                  {/* Acceso Consola Administrador */}
                  {user.rol === 'administrador' && (
                    <Link
                      to="/admin/users"
                      title="Consola Administrador"
                      className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 select-none ${
                        location.pathname.startsWith('/admin')
                          ? 'bg-gradient-to-r from-purple-100/80 via-indigo-100/70 to-violet-100/80 text-purple-800 font-semibold border border-purple-300/80 shadow-xs'
                          : 'bg-gradient-to-r from-purple-50/50 via-indigo-50/40 to-violet-50/50 hover:from-purple-100/70 hover:via-indigo-100/60 hover:to-violet-100/70 text-slate-700 hover:text-purple-800 border border-purple-200/60 hover:border-purple-300/90 shadow-xs hover:shadow-sm'
                      }`}
                    >
                      <ShieldCheck className="w-4 h-4 text-purple-600" />
                      <span className="hidden lg:inline">Admin</span>
                    </Link>
                  )}

                  {/* Acceso Consola Docente */}
                  {(user.rol === 'docente' || user.rol === 'administrador') && (
                    <Link
                      to="/teacher/cases"
                      title="Consola Docente"
                      className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 select-none ${
                        location.pathname.startsWith('/teacher')
                          ? 'bg-gradient-to-r from-blue-100/80 via-sky-100/70 to-indigo-100/80 text-blue-800 font-semibold border border-blue-300/80 shadow-xs'
                          : 'bg-gradient-to-r from-cyan-50/50 via-blue-50/40 to-indigo-50/50 hover:from-cyan-100/70 hover:via-blue-100/60 hover:to-indigo-100/70 text-slate-700 hover:text-blue-800 border border-blue-200/60 hover:border-blue-300/90 shadow-xs hover:shadow-sm'
                      }`}
                    >
                      <UserCheck className="w-4 h-4 text-blue-600" />
                      <span className="hidden lg:inline">Docente</span>
                    </Link>
                  )}

                  {/* Bandeja de Notificaciones (Visible en escritorio / En móvil vive en la barra inferior) */}
                  <div className="hidden md:block">
                    <NotificationsDropdown />
                  </div>

                  {/* Menú Desplegable de Perfil (Oculto en cabecera móvil si está en catálogo, ya que se renderiza en la barra inferior) */}
                  <div className={isCatalogRoute ? 'hidden md:block' : 'block'}>
                    <UserProfileDropdown />
                  </div>
                </>
              ) : location.pathname === '/login' ? (
                <Link
                  to="/register"
                  className="px-3 sm:px-4 py-1.5 sm:py-2 text-[#0b57d0] hover:bg-blue-50 rounded-full text-xs font-medium transition-colors"
                >
                  Crear cuenta
                </Link>
              ) : (
                <Link
                  to="/login"
                  className="px-3 sm:px-4 py-1.5 sm:py-2 bg-[#0b57d0] hover:bg-blue-700 text-white rounded-full text-xs font-medium transition-colors"
                >
                  Iniciar Sesión
                </Link>
              )}
            </div>
          </>
        )}
      </div>

      {/* Modal Desacoplado: Unirse a Sala Colaborativa */}
      <JoinRoomModal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
      />

      {/* Barra de Navegación Inferior Móvil (Exclusiva del Catálogo de Casos) */}
      <MobileBottomNav
        onOpenSearch={() => setShowMobileSearch(true)}
        onOpenJoinRoom={() => setShowJoinModal(true)}
      />
    </header>
  );
}
