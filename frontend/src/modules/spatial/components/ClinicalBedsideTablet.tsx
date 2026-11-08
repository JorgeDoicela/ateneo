import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Heart,
  Activity,
  Wind,
  Thermometer,
  ShieldAlert,
  ArrowRight,
  ClipboardList
} from 'lucide-react';
import { useSpatialStore } from '../store/useSpatialStore';
import { useCases } from '../../cases/hooks/useCases';

export const ClinicalBedsideTablet: React.FC = () => {
  const navigate = useNavigate();
  const { cases } = useCases();

  const isTabletOpen = useSpatialStore((s) => s.isTabletOpen);
  const activeBedId = useSpatialStore((s) => s.activeBedId);
  const beds = useSpatialStore((s) => s.beds);
  const closeBedInspection = useSpatialStore((s) => s.closeBedInspection);

  if (!isTabletOpen || !activeBedId) return null;

  const activeBed = beds.find((b) => b.id === activeBedId);
  if (!activeBed) return null;

  const clinicalCase = cases?.find((c) => c.id === activeBed.caseId);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-slate-950/70 backdrop-blur-sm animate-fadeIn select-text">
      <div className="relative w-full max-w-2xl bg-white rounded-[28px] shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[88vh]">
        {/* Cabecera de la Tableta: Ateneo+ Minimalista */}
        <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ClipboardList className="w-5 h-5 text-[#0b57d0] shrink-0" />
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-semibold text-slate-900 tracking-tight">
                  Cama {activeBed.bedNumber}: {activeBed.label}
                </h2>
                {activeBed.urgency === 'codigo_rojo' && (
                  <span className="text-[11px] font-bold text-red-600 animate-pulse">
                    • CÓDIGO ROJO
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">
                Expediente Clínico de Urgencias • Guía de Práctica Clínica MSP Ecuador
              </p>
            </div>
          </div>

          <button
            onClick={closeBedInspection}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-full transition-colors"
            title="Cerrar expediente"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Panel de Signos Vitales de Telemetría */}
        <div className="bg-[#f0f4f9] border-b border-slate-100 px-6 py-3.5 grid grid-cols-2 sm:grid-cols-5 gap-3">
          <div className="bg-white p-2.5 rounded-[18px] border border-slate-200/60 shadow-xs flex items-center space-x-2.5">
            <Heart className="w-4 h-4 text-red-500 shrink-0" />
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">FC</p>
              <p className="text-sm font-bold text-slate-900">{activeBed.vitals.hr} <span className="text-[10px] font-normal text-slate-500">lpm</span></p>
            </div>
          </div>

          <div className="bg-white p-2.5 rounded-[18px] border border-slate-200/60 shadow-xs flex items-center space-x-2.5">
            <Activity className="w-4 h-4 text-[#0b57d0] shrink-0" />
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">PA</p>
              <p className="text-sm font-bold text-slate-900">{activeBed.vitals.bp} <span className="text-[10px] font-normal text-slate-500">mmHg</span></p>
            </div>
          </div>

          <div className="bg-white p-2.5 rounded-[18px] border border-slate-200/60 shadow-xs flex items-center space-x-2.5">
            <Wind className="w-4 h-4 text-cyan-600 shrink-0" />
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">FR</p>
              <p className="text-sm font-bold text-slate-900">{activeBed.vitals.rr} <span className="text-[10px] font-normal text-slate-500">rpm</span></p>
            </div>
          </div>

          <div className="bg-white p-2.5 rounded-[18px] border border-slate-200/60 shadow-xs flex items-center space-x-2.5">
            <Activity className="w-4 h-4 text-emerald-600 shrink-0" />
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">SatO2</p>
              <p className="text-sm font-bold text-slate-900">{activeBed.vitals.spo2}%</p>
            </div>
          </div>

          <div className="bg-white p-2.5 rounded-[18px] border border-slate-200/60 shadow-xs flex items-center space-x-2.5 col-span-2 sm:col-span-1">
            <Thermometer className="w-4 h-4 text-amber-500 shrink-0" />
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-semibold">Temp</p>
              <p className="text-sm font-bold text-slate-900">{activeBed.vitals.temp} °C</p>
            </div>
          </div>
        </div>

        {/* Cuerpo del Expediente Clínico */}
        <div className="p-6 overflow-y-auto space-y-4 text-sm text-slate-700">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
              Cuadro Clínico y Anamnesis
            </h3>
            <p className="leading-relaxed bg-[#f0f4f9] p-4 rounded-[20px] border border-slate-200/60 text-slate-800">
              {clinicalCase?.enunciado || clinicalCase?.caso_preambulo || 'Cargando información clínica del paciente...'}
            </p>
          </div>

          {clinicalCase?.pregunta && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                Interrogante Formativa
              </h3>
              <p className="leading-relaxed bg-[#f0f4f9] p-4 rounded-[20px] border border-slate-200/60 text-xs text-slate-800">
                {clinicalCase.pregunta}
              </p>
            </div>
          )}

          {activeBed.urgency === 'codigo_rojo' && (
            <div className="p-4 bg-red-50 border border-red-200/80 rounded-[20px] flex items-start space-x-3 text-red-900 text-xs">
              <ShieldAlert className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Prioridad de Triaje Absoluta:</span> Paciente en estado crítico según algoritmo de choque obstétrico / emergencias vitales del MSP. Se requiere intervención diagnóstica y terapéutica inmediata.
              </div>
            </div>
          )}
        </div>

        {/* Pie con Acción Formativa */}
        <div className="px-6 py-4 bg-white border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={closeBedInspection}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-full transition-colors"
          >
            Volver a la Sala
          </button>

          <button
            onClick={() => {
              closeBedInspection();
              navigate(`/cases/${activeBed.caseId}`);
            }}
            className="py-2.5 px-6 bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 hover:from-cyan-700 hover:via-blue-700 hover:to-indigo-700 text-white font-medium text-xs rounded-full transition-all shadow-md shadow-blue-500/20 active:scale-[0.99] flex items-center gap-2 cursor-pointer"
          >
            <span>Iniciar Resolución Diagnóstica</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClinicalBedsideTablet;
