import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { UserCheck, FileText, BarChart3 } from 'lucide-react';

/**
 * Layout de Supervisión y Docencia Médica (Ateneo+)
 * Ofrece encabezado contextual y navegación por sub-rutas / pestañas
 * para aislar responsabilidades de moderación de salas y analítica psicométrica.
 */
export const TeacherLayout: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn pb-12">
      {/* Encabezado General del Módulo Docente */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-2 border-b border-slate-200/80">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#0b57d0] uppercase tracking-wider mb-1.5">
            <UserCheck className="w-4 h-4" />
            <span>Supervisión y Docencia Médica • MSP Ecuador</span>
          </div>
          <h1 className="text-[28px] sm:text-[34px] font-normal tracking-tight text-[#1f1f1f] font-heading">
            Panel de Docentes y Tutores Clínicos
          </h1>
          <p className="text-xs sm:text-sm text-[#444746] mt-0.5 max-w-2xl leading-relaxed">
            Supervisión pedagógica del razonamiento diagnóstico en la cohorte y moderación de salas clínicas sincrónicas.
          </p>
        </div>
      </div>

      {/* Sub-navegación por Pestañas Clínicas (Material 3 Canvas) */}
      <nav aria-label="Secciones de docencia" className="flex items-center gap-2 border-b border-slate-200/80 pb-3">
        <NavLink
          to="/teacher/cases"
          className={({ isActive }) =>
            `flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
              isActive
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`
          }
        >
          <FileText className="w-4 h-4" />
          <span>Casos y Salas Clínicas</span>
        </NavLink>

        <NavLink
          to="/teacher/analytics"
          className={({ isActive }) =>
            `flex items-center gap-2 px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer ${
              isActive
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`
          }
        >
          <BarChart3 className="w-4 h-4" />
          <span>Analítica de Cohorte</span>
        </NavLink>
      </nav>

      {/* Vista de Sub-ruta Activa */}
      <Outlet />
    </div>
  );
};

export default TeacherLayout;
