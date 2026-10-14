import { ReactNode } from 'react';
import { Navigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { ShieldAlert } from 'lucide-react';
import type { UserRole } from '../../../types';

export interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: UserRole[];
}

/**
 * ProtectedRoute — Guardián de navegación con verificación de rol (RBAC)
 */
export default function ProtectedRoute({ children, allowedRoles = [] }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center gap-3">
        <div className="w-10 h-10 border-4 border-sky-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-semibold text-slate-600">Verificando sesión y permisos...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.rol)) {
    const fallbackPath = user.rol === 'docente' ? '/teacher' : user.rol === 'administrador' ? '/admin' : '/';
    return (
      <div className="max-w-md mx-auto my-12 bg-white rounded-[28px] p-8 text-center shadow-xs">
        <ShieldAlert className="w-10 h-10 text-rose-600 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-slate-900 mb-2 font-heading">Acceso Restringido</h3>
        <p className="text-sm text-slate-600 mb-6 leading-relaxed">
          Tu rol de <strong className="text-slate-800">{user.rol}</strong> no posee los permisos necesarios para acceder a esta sección.
        </p>
        <div className="flex justify-center">
          <Link
            to={fallbackPath}
            className="inline-flex items-center justify-center px-6 py-2.5 rounded-full text-sm font-medium bg-slate-900 text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            Volver a mi espacio
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
