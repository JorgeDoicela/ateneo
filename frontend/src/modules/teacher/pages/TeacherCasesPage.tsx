import React, { useEffect, useState } from 'react';
import { Plus, ArrowRight, Loader2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import casesApi from '../../cases/api/casesApi';
import collaborationApi from '../../collaboration/api/collaborationApi';
import ClinicalButton from '../../../core/ui/ClinicalButton';
import type { ExtendedClinicalCase } from '../../cases/hooks/useCases';
import { resolveGpcMeta } from '../../cases/hooks/useCases';

/**
 * Vista de Casos y Creación de Salas Clínicas Sincrónicas (Ateneo+)
 * Permite a los docentes moderar ateneos y simular casos en tiempo real.
 */
export const TeacherCasesPage: React.FC = () => {
  const { user } = useAuth();
  const [cases, setCases] = useState<ExtendedClinicalCase[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [creatingRoomId, setCreatingRoomId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setErrorMsg(null);
      try {
        const data = await casesApi.getCases();
        setCases(data as ExtendedClinicalCase[]);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Error al cargar catálogo de casos';
        setErrorMsg(msg);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleCreateAteneoRoom = async (caseId: string) => {
    setCreatingRoomId(caseId);
    setErrorMsg(null);
    try {
      const room = await collaborationApi.createRoom(
        caseId,
        user?.id || 'usr_docente_001',
        user?.nombre ? `${user.nombre} (Docente)` : 'Dr. Carlos Andrade (Docente)'
      );
      const targetCode = room.room_code || room.codigo || '';
      navigate(`/ateneo/${targetCode}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al crear sala de Ateneo';
      setErrorMsg(msg);
    } finally {
      setCreatingRoomId(null);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-slate-800">
            Catálogo de Casos para Ateneo Sincrónico
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Selecciona un caso clínico para moderar una sala de consenso o inspeccionar las fases diagnósticas.
          </p>
        </div>
        <span className="text-xs font-medium text-[#747775] bg-[#f0f4f9] px-3 py-1 rounded-full">
          {cases.length} casos disponibles
        </span>
      </div>

      {errorMsg && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-xs text-rose-800">
          {errorMsg}
        </div>
      )}

      {loading ? (
        <div className="py-12 flex flex-col items-center justify-center gap-2 text-xs text-slate-500">
          <Loader2 className="w-6 h-6 animate-spin text-[#0b57d0]" />
          <span>Cargando catálogo de casos clínicos...</span>
        </div>
      ) : cases.length === 0 ? (
        <div className="text-center py-12 text-xs text-slate-400 bg-white rounded-[28px] border border-slate-200/80">
          No hay casos clínicos disponibles en la cohorte.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cases.map((c) => (
            <div
              key={c.id}
              className="bg-white rounded-[28px] p-6 shadow-xs border border-slate-200/80 hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-semibold ${resolveGpcMeta(c.guia_asociada || c.gpc_referencia).isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                    {resolveGpcMeta(c.guia_asociada || c.gpc_referencia).label}
                  </span>
                  {c.fases && (
                    <span className="text-[11px] text-[#747775] font-medium">{c.fases.length} Fases</span>
                  )}
                </div>
                <h3 className="text-base font-medium text-[#1f1f1f] font-heading line-clamp-2">
                  {c.titulo}
                </h3>
                <p className="text-xs text-[#444746] line-clamp-3 leading-relaxed">
                  {c.enunciado || c.caso_preambulo}
                </p>
              </div>

              <div className="pt-5 border-t border-slate-100 flex items-center justify-between mt-4">
                <Link
                  to={`/cases/${c.id}`}
                  className="text-xs font-medium text-[#444746] hover:text-[#0b57d0] flex items-center gap-1 transition-colors"
                >
                  <span>Inspeccionar</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>

                <ClinicalButton
                  variant="primary"
                  size="sm"
                  loading={creatingRoomId === c.id}
                  onClick={() => handleCreateAteneoRoom(c.id)}
                  icon={Plus}
                >
                  Crear Sala Ateneo
                </ClinicalButton>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TeacherCasesPage;
