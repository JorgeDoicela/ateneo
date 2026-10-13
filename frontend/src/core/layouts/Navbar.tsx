import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Award, ShieldCheck, UserCheck, TrendingUp, Users, BookOpen } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import GlobalSearchBar from './components/GlobalSearchBar';
import ConnectivityBadge from './components/ConnectivityBadge';
import UserProfileDropdown from './components/UserProfileDropdown';
import JoinRoomModal from '../../modules/collaboration/components/JoinRoomModal';

/**
 * Navbar — Cabecera principal desacoplada y fijada superior (Liquid Glassmorphism)
 * Orquestador modular de alta cohesión:
 * - Brand Logo & Slogan
 * - GlobalSearchBar (Cápsula de búsqueda autónoma)
 * - ConnectivityBadge (Buffer offline y sincronización hospitalaria)
 * - Enlaces RBAC (Benchmark, Desempeño, Admin, Docente)
 * - UserProfileDropdown (Menú de identidad institucional y sesión)
 */
export default function Navbar() {
  const { user } = useAuth();
  const location = useLocation();
  const [showJoinModal, setShowJoinModal] = useState(false);
  const isAnalyticsView = location.pathname === '/analytics' || location.pathname === '/performance';

  return (
    <header className="bg-white/85 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50 transition-colors w-full">
      <div className="w-full max-w-[1680px] mx-auto px-4 sm:px-8 lg:px-12 h-16 flex items-center justify-between gap-4">
        
        {/* 1. Logo & Identidad de Marca Ateneo+ */}
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

        {/* 2. Barra de Búsqueda Global Desacoplada */}
        <GlobalSearchBar />

        {/* 3. Navegación, Conectividad Clínica y Perfil */}
        <div className="flex items-center gap-3 text-xs font-medium text-[#444746] shrink-0">
          {/* Indicador de Conectividad & Sincronización Offline */}
          <ConnectivityBadge />

          {user ? (
            <>
              {/* Enlace Dinámico Desempeño / Catálogo */}
              <Link
                to={isAnalyticsView ? '/cases' : '/analytics'}
                title={isAnalyticsView ? 'Volver al Catálogo de Casos' : 'Mi Desempeño y Tendencias Clínicas'}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-colors ${
                  isAnalyticsView
                    ? 'bg-sky-50 text-[#0b57d0] font-semibold hover:bg-sky-100/80'
                    : 'text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100'
                }`}
              >
                {isAnalyticsView ? (
                  <>
                    <BookOpen className="w-4 h-4 text-[#0b57d0]" />
                    <span className="inline">Catálogo</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4 text-[#0b57d0]" />
                    <span className="inline">Desempeño</span>
                  </>
                )}
              </Link>

              {/* Botón Unirse a Sala Colaborativa */}
              <button
                type="button"
                onClick={() => setShowJoinModal(true)}
                title="Unirse a Sala de Ateneo"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-colors text-[#444746] hover:text-[#1f1f1f] hover:bg-slate-100 cursor-pointer"
              >
                <Users className="w-4 h-4 text-[#0b57d0]" />
                <span>Unirse a Sala</span>
              </button>

              {/* Enlace Benchmark (Restringido a Administradores) */}
              {user.rol === 'administrador' && (
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
              )}

              {/* Acceso Consola Administrador */}
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

              {/* Acceso Consola Docente */}
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

              {/* Menú Desplegable de Perfil */}
              <UserProfileDropdown />
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

      {/* Modal Desacoplado: Unirse a Sala Colaborativa */}
      <JoinRoomModal
        isOpen={showJoinModal}
        onClose={() => setShowJoinModal(false)}
      />
    </header>
  );
}
