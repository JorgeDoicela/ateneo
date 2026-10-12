import React, { useEffect, useState } from 'react';
import { Users, Database, Server, RefreshCw, UserCheck, ShieldCheck, GraduationCap } from 'lucide-react';
import { authApi } from '../../auth/api/authApi';
import type { User } from '../../../types';

/**
 * Vista de Gestión de Usuarios y Roles RBAC (Ateneo+)
 * Permite auditar las cuentas registradas en la institución y monitorear el estado del motor RAG.
 */
export const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await authApi.getUsers();
      setUsers(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al cargar lista de usuarios';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Botón de Actualización y Subtítulo */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-800">
            Directorio Institucional y Roles Asignados
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitoreo en tiempo real de cuentas activas en la cohorte y conectividad del clúster.
          </p>
        </div>
        <button
          onClick={loadUsers}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-[#1f1f1f] text-xs font-medium rounded-full transition-colors shadow-xs cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#0b57d0] ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Cuentas</span>
        </button>
      </div>

      {/* Tarjetas de Resumen de Infraestructura */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white rounded-[24px] p-6 shadow-xs border border-slate-200/80 flex items-center justify-between">
          <div>
            <span className="text-xs text-[#747775] font-medium block mb-1">Usuarios Registrados</span>
            <p className="text-3xl font-normal text-[#1f1f1f] font-heading">{users.length}</p>
            <span className="text-[11px] text-emerald-600 font-medium mt-1 inline-block">Cuentas activas en cohorte</span>
          </div>
          <div className="w-12 h-12 rounded-full bg-purple-50 text-purple-700 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-[24px] p-6 shadow-xs border border-slate-200/80 flex items-center justify-between">
          <div>
            <span className="text-xs text-[#747775] font-medium block mb-1">Motor Vectorial</span>
            <p className="text-2xl font-normal text-[#1f1f1f] font-heading">ChromaDB</p>
            <span className="text-[11px] text-[#0b57d0] font-medium mt-1 inline-block">GPC MSP Indexadas</span>
          </div>
          <div className="w-12 h-12 rounded-full bg-sky-50 text-[#0b57d0] flex items-center justify-center">
            <Database className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white rounded-[24px] p-6 shadow-xs border border-slate-200/80 flex items-center justify-between">
          <div>
            <span className="text-xs text-[#747775] font-medium block mb-1">Servidor de Inferencia</span>
            <p className="text-2xl font-normal text-[#1f1f1f] font-heading">FastAPI + LLM</p>
            <span className="text-[11px] text-emerald-600 font-medium mt-1 inline-block">Conexión Segura TLS</span>
          </div>
          <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <Server className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Tabla de Usuarios Material 3 */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/80 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-semibold text-[#1f1f1f]">Usuarios y Roles de Acceso (RBAC)</h3>
            <p className="text-xs text-[#444746] mt-0.5">Control de credenciales y roles asignados en el simulador clínico.</p>
          </div>
          <span className="text-xs font-medium text-[#747775] bg-[#f0f4f9] px-3 py-1 rounded-full">
            {users.length} registros
          </span>
        </div>

        {error ? (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-[16px] text-xs text-rose-800">
            {error}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#444746]">
              <thead className="bg-[#f0f4f9] text-[#1f1f1f] font-medium uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="px-5 py-3.5 rounded-l-[12px]">Nombre y Apellidos</th>
                  <th className="px-5 py-3.5">Correo Institucional</th>
                  <th className="px-5 py-3.5">Rol en Plataforma</th>
                  <th className="px-5 py-3.5 text-right rounded-r-[12px]">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => {
                  let badge = 'bg-sky-50 text-[#0b57d0]';
                  let Icon = GraduationCap;
                  if (u.rol === 'docente') {
                    badge = 'bg-amber-50 text-amber-800';
                    Icon = UserCheck;
                  } else if (u.rol === 'administrador') {
                    badge = 'bg-purple-50 text-purple-800';
                    Icon = ShieldCheck;
                  }

                  return (
                    <tr key={u.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-5 py-4 font-medium text-[#1f1f1f]">{u.nombre}</td>
                      <td className="px-5 py-4 text-[#747775]">{u.email}</td>
                      <td className="px-5 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${badge}`}>
                          <Icon className="w-3.5 h-3.5" />
                          <span className="capitalize">{u.rol}</span>
                        </span>
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="text-xs text-emerald-600 font-medium">Activo</span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUsersPage;
