import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { ShieldCheck, Users, Link2 } from 'lucide-react';

/**
 * Layout de Administración Institucional (Ateneo+)
 * Ofrece encabezado contextual y navegación por sub-rutas / pestañas
 * para aislar responsabilidades de RBAC, Magic Links y gobernanza.
 */
export const AdminLayout: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Encabezado General del Módulo de Administración */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-purple-700 uppercase tracking-wider mb-1.5">
            <ShieldCheck className="w-4 h-4" />
            <span>Consola de Gestión y Seguridad • GPC Ecuador</span>
          </div>
          <h1 className="text-[28px] sm:text-[34px] font-normal tracking-tight text-[#1f1f1f] font-heading">
            Panel de Administración
          </h1>
          <p className="text-xs sm:text-sm text-[#444746] mt-0.5 max-w-2xl leading-relaxed">
            Gobernanza institucional de identidades clínicas, emisión de accesos sin fricción y auditoría de plataforma.
          </p>
        </div>
      </div>

      {/* Sub-navegación por Pestañas Clínicas (Material 3 Canvas) */}
      <nav aria-label="Secciones de administración" className="flex items-center gap-2 border-b border-slate-200/80 pb-3">
        <NavLink
          to="/admin/users"
          className={({ isActive }) =>
            `flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
              isActive
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`
          }
        >
          <Users className="w-4 h-4" />
          <span>Usuarios y Roles (RBAC)</span>
        </NavLink>

        <NavLink
          to="/admin/magic-links"
          className={({ isActive }) =>
            `flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
              isActive
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`
          }
        >
          <Link2 className="w-4 h-4" />
          <span>Magic Links e Invitaciones</span>
        </NavLink>
      </nav>

      {/* Vista de Sub-ruta Activa */}
      <Outlet />
    </div>
  );
};

export default AdminLayout;
