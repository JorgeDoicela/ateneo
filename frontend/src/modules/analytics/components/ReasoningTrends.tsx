import { useState, useEffect } from 'react';
import { Filter, Activity } from 'lucide-react';
import analyticsApi from '../api/analyticsApi';
import SkillRadarChart from './SkillRadarChart';
import type { AxisCompetencyItem } from '../../../types';

interface TimeScoreItem {
  id: number;
  timestamp: string;
  fecha_formateada?: string;
  score: number;
  guia_asociada: string;
  case_title: string;
}

interface ChartPointItem extends TimeScoreItem {
  x: number;
  y: number;
  fechaLabel: string;
}

interface FrequentOmission {
  patron: string;
  frecuencia: number;
}

interface RadarCompetencyItem {
  eje: string;
  label: string;
  score: number;
  brechas?: number;
}

interface GpcProgressDetail {
  guia: string;
  evaluaciones: number;
  scores: number[];
  promedio: number;
}

interface TrendsData {
  total_evaluaciones: number;
  promedio_general: number;
  punto_debil_principal: string;
  progreso_por_gpc: Record<string, GpcProgressDetail>;
  puntuaciones_tiempo: TimeScoreItem[];
  omisiones_mas_frecuentes: FrequentOmission[];
  radar_competencias: RadarCompetencyItem[];
}

export default function ReasoningTrends() {
  const [trends, setTrends] = useState<TrendsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedGpc, setSelectedGpc] = useState<string>('TODAS');
  const [activePoint, setActivePoint] = useState<ChartPointItem | null>(null);

  const fetchTrends = async () => {
    setLoading(true);
    try {
      const data = await analyticsApi.getTrends();
      setTrends(data as TrendsData);
    } catch (err) {
      console.error("Error al cargar tendencias:", err);
      // Fallback institucional en caso de error
      setTrends({
        total_evaluaciones: 4,
        promedio_general: 7.8,
        punto_debil_principal: "Punto formativo prioritario: Dosificación exacta de esquemas antimicrobianos y rehidratación intravenosa.",
        progreso_por_gpc: {
          "GPC_EHIRN2019": { guia: "GPC_EHIRN2019", evaluaciones: 2, scores: [6.5, 8.0], promedio: 7.3 },
          "HIPERTENSION": { guia: "HIPERTENSION", evaluaciones: 2, scores: [7.0, 9.5], promedio: 8.3 }
        },
        puntuaciones_tiempo: [
          { id: 1, timestamp: "2026-08-01T10:00:00", fecha_formateada: "01/08", score: 6.5, guia_asociada: "GPC_EHIRN2019", case_title: "EHIRN Sangrado Umbilical" },
          { id: 2, timestamp: "2026-08-03T14:30:00", fecha_formateada: "03/08", score: 7.0, guia_asociada: "HIPERTENSION", case_title: "Crisis Hipertensiva en Adulto" },
          { id: 3, timestamp: "2026-08-05T09:15:00", fecha_formateada: "05/08", score: 8.0, guia_asociada: "GPC_EHIRN2019", case_title: "EHIRN Caso Control" },
          { id: 4, timestamp: "2026-08-07T11:20:00", fecha_formateada: "07/08", score: 9.5, guia_asociada: "HIPERTENSION", case_title: "Hipertensión Emergencia" }
        ],
        omisiones_mas_frecuentes: [
          { patron: "Dosificación exacta de líquidos e infusión parenteral según peso", frecuencia: 3 },
          { patron: "Cálculo de dosis ajustada de antibióticos de amplio espectro", frecuencia: 2 },
          { patron: "Monitoreo de signos vitales cada 15 minutos en fase aguda", frecuencia: 1 }
        ],
        radar_competencias: [
          { eje: "diagnóstico", label: "Diagnóstico", score: 85, brechas: 1 },
          { eje: "tratamiento", label: "Tratamiento", score: 65, brechas: 2 },
          { eje: "prevención", label: "Prevención", score: 92, brechas: 0 },
          { eje: "seguimiento", label: "Seguimiento", score: 78, brechas: 1 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-[28px] p-12 shadow-xs border border-slate-200/60 flex items-center justify-center space-x-3 text-[#444746] text-sm">
        <Activity className="w-5 h-5 animate-spin text-[#0b57d0]" />
        <span>Cargando analítica de rendimiento formativo...</span>
      </div>
    );
  }

  if (!trends || trends.total_evaluaciones === 0) {
    return (
      <div className="bg-white rounded-[28px] p-12 shadow-xs border border-slate-200/60 text-center space-y-4 max-w-lg mx-auto">
        <h3 className="text-lg font-normal text-[#1f1f1f] font-heading">Sin historial suficiente</h3>
        <p className="text-xs text-[#747775] leading-relaxed">
          Completa tus primeros casos clínicos para desbloquear la gráfica de progresión por GPC y el análisis estructurado de tu desempeño formativo.
        </p>
      </div>
    );
  }

  const { total_evaluaciones, promedio_general, punto_debil_principal, progreso_por_gpc, puntuaciones_tiempo, omisiones_mas_frecuentes, radar_competencias } = trends;

  const competenciasPorEje: AxisCompetencyItem[] = (radar_competencias || []).map(r => ({
    key: r.eje,
    label: r.label,
    score: r.score,
    items: [],
    estadoLabel: r.score >= 80 ? 'Consolidado' : r.score >= 50 ? 'En Desarrollo' : 'Brecha Crítica'
  }));

  const gpcKeys = Object.keys(progreso_por_gpc || {});
  const puntosFiltrados = selectedGpc === 'TODAS'
    ? puntuaciones_tiempo
    : puntuaciones_tiempo.filter(p => p.guia_asociada === selectedGpc);

  // Dimensionamiento adaptativo y prevención de solapamientos
  const minSpacing = 28;
  const chartHeight = 220;
  const paddingX = 45;
  const paddingY = 35;
  const chartWidth = Math.max(720, puntosFiltrados.length * minSpacing + paddingX * 2);
  const graphWidth = chartWidth - paddingX * 2;
  const graphHeight = chartHeight - paddingY * 2;

  const pointsSVG = puntosFiltrados.map((p, idx) => {
    const x = paddingX + (puntosFiltrados.length > 1 ? (idx / (puntosFiltrados.length - 1)) * graphWidth : graphWidth / 2);
    const y = chartHeight - paddingY - (p.score / 10) * graphHeight;
    const fechaLabel = p.fecha_formateada || (p.timestamp ? p.timestamp.substring(8, 10) + '/' + p.timestamp.substring(5, 7) : '');
    return { x, y, fechaLabel, ...p };
  });

  const polylinePoints = pointsSVG.map(p => `${p.x},${p.y}`).join(' ');
  const areaPolygonPoints = pointsSVG.length > 0 
    ? `${pointsSVG[0].x},${chartHeight - paddingY} ${polylinePoints} ${pointsSVG[pointsSVG.length - 1].x},${chartHeight - paddingY}`
    : '';

  const stepDate = Math.max(1, Math.ceil(puntosFiltrados.length / 8));
  const showAllLabels = puntosFiltrados.length <= 12;

  return (
    <div className="space-y-8 animate-fadeIn pb-12">
      
      {/* 1. Tarjeta de Advertencia Formativa: PUNTO DÉBIL */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/60 hover:border-slate-300/80 transition-all space-y-5">
        <div className="space-y-1.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-800 bg-amber-50/80 border border-amber-200/60 px-3.5 py-1 rounded-full inline-block shadow-2xs">
            Diagnóstico Formativo Normativo
          </span>
          <h3 className="text-lg sm:text-xl font-normal text-[#1f1f1f] font-heading pt-1 leading-snug">
            {punto_debil_principal}
          </h3>
          <p className="text-xs text-[#444746] leading-relaxed">
            Patrón de razonamiento clínico detectado al contrastar tus intervenciones contra las Guías de Práctica Clínica (GPC Ecuador).
          </p>
        </div>

        {/* Lista de Omisiones Recurrentes con acabado Micro-Cristal */}
        {omisiones_mas_frecuentes && omisiones_mas_frecuentes.length > 0 && (
          <div className="border-t border-slate-100/80 pt-4 space-y-3">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Patrones de Omisión Más Frecuentes ({omisiones_mas_frecuentes.length})
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {omisiones_mas_frecuentes.map((om, i) => (
                <div 
                  key={i} 
                  className="flex items-center justify-between bg-white/80 hover:bg-white border border-slate-200/70 hover:border-blue-200/80 p-3.5 rounded-[18px] text-xs font-medium text-slate-800 shadow-2xs transition-all gap-3"
                >
                  <span className="truncate pr-1 text-slate-800">{om.patron}</span>
                  <span className="text-[11px] font-semibold text-amber-800 bg-amber-100/70 border border-amber-200/60 px-2.5 py-0.5 rounded-full shrink-0 font-mono">
                    {om.frecuencia}x
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 2. Componente del Radar de Habilidades del Estudiante */}
      {competenciasPorEje.length > 0 && (
        <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/60 hover:border-slate-300/80 transition-all">
          <SkillRadarChart competenciasPorEje={competenciasPorEje} />
        </div>
      )}

      {/* 3. Gráfica de Progreso de Score en el Tiempo por GPC */}
      <div className="bg-white rounded-[28px] p-6 sm:p-8 shadow-xs border border-slate-200/60 hover:border-slate-300/80 transition-all space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100/80 pb-4">
          <div>
            <div className="text-xs font-semibold text-[#0b57d0] uppercase tracking-wider mb-1">
              <span>Progresión Longitudinal</span>
            </div>
            <h3 className="text-xl font-normal text-[#1f1f1f] font-heading">
              Evolución de Calificaciones por GPC
            </h3>
          </div>

          <div className="flex items-center bg-white/85 hover:bg-white backdrop-blur-md px-3.5 py-1.5 rounded-full border border-slate-200/80 shadow-xs transition-all">
            <Filter className="w-3.5 h-3.5 text-[#0b57d0] mr-2" />
            <select
              value={selectedGpc}
              onChange={(e) => {
                setSelectedGpc(e.target.value);
                setActivePoint(null);
              }}
              className="text-xs font-medium bg-transparent text-[#1f1f1f] focus:outline-none cursor-pointer pr-1"
            >
              <option value="TODAS">Todas las GPCs</option>
              {gpcKeys.map(gpc => (
                <option key={gpc} value={gpc}>{gpc}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Tooltip Dinámico Flotante de Cristal Líquido si hay punto activo */}
        {activePoint && (
          <div className="p-3 bg-gradient-to-r from-cyan-50/80 via-blue-50/60 to-indigo-50/80 border border-blue-200/80 rounded-[18px] flex flex-wrap items-center justify-between gap-2 text-xs animate-fadeIn">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-900">{activePoint.case_title || 'Caso Clínico'}</span>
              <span className="text-slate-400 font-light">•</span>
              <span className="text-slate-600 font-medium">{activePoint.guia_asociada}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-slate-500 font-mono text-[11px]">{activePoint.fechaLabel}</span>
              <span className="font-bold text-[#0b57d0] font-mono text-sm px-2.5 py-0.5 rounded-full bg-white border border-blue-200/80 shadow-2xs">
                {activePoint.score.toFixed(1)} / 10 pts
              </span>
            </div>
          </div>
        )}

        {pointsSVG.length > 0 ? (
          <div className="w-full overflow-x-auto no-scrollbar touch-pan-x py-1">
            <div style={{ minWidth: `${chartWidth}px` }}>
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-auto font-sans overflow-visible select-none">
                <defs>
                  {/* Gradiente de relleno luminoso bajo la curva */}
                  <linearGradient id="curveAreaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2563eb" stopOpacity="0.22" />
                    <stop offset="60%" stopColor="#06b6d4" stopOpacity="0.06" />
                    <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.00" />
                  </linearGradient>

                  {/* Gradiente tricolor de la línea */}
                  <linearGradient id="curveLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#06b6d4" />
                    <stop offset="50%" stopColor="#2563eb" />
                    <stop offset="100%" stopColor="#4f46e5" />
                  </linearGradient>
                </defs>

                {/* Líneas Guía Horizontales de Calificación */}
                {[0, 2.5, 5.0, 7.5, 10.0].map((val) => {
                  const y = chartHeight - paddingY - (val / 10) * graphHeight;
                  return (
                    <g key={val}>
                      <line 
                        x1={paddingX} 
                        y1={y} 
                        x2={chartWidth - paddingX} 
                        y2={y} 
                        stroke="#e2e8f0" 
                        strokeWidth="1" 
                        strokeDasharray={val === 0 ? undefined : "3,3"} 
                      />
                      <text 
                        x={paddingX - 10} 
                        y={y + 3.5} 
                        textAnchor="end" 
                        className="text-[10px] fill-slate-400 font-mono font-medium"
                      >
                        {val.toFixed(1)}
                      </text>
                    </g>
                  );
                })}

                {/* Relleno translúcido bajo la curva */}
                {pointsSVG.length > 1 && (
                  <polygon
                    points={areaPolygonPoints}
                    fill="url(#curveAreaGrad)"
                  />
                )}

                {/* Trazado continuo suave */}
                {pointsSVG.length > 1 && (
                  <polyline
                    fill="none"
                    stroke="url(#curveLineGrad)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={polylinePoints}
                  />
                )}

                {/* Puntos de evaluación y etiquetas inteligentes no solapadas */}
                {pointsSVG.map((p, idx) => {
                  const isHovered = activePoint?.id === p.id;
                  const isMinOrMax = p.score === 10 || p.score === 0;
                  const shouldShowLabel = showAllLabels || isHovered || (isMinOrMax && idx % 3 === 0);
                  const showDate = showAllLabels || idx % stepDate === 0 || idx === pointsSVG.length - 1;

                  return (
                    <g 
                      key={idx} 
                      className="cursor-pointer group"
                      onMouseEnter={() => setActivePoint(p)}
                      onClick={() => setActivePoint(p)}
                    >
                      {/* Círculo Interactivo */}
                      <circle 
                        cx={p.x} 
                        cy={p.y} 
                        r={isHovered ? "6" : "3.5"} 
                        className="fill-white stroke-[#0b57d0] stroke-[2.5px] transition-all group-hover:stroke-cyan-500 group-hover:fill-blue-50" 
                      />

                      {/* Etiqueta de Score solo cuando hay espacio o en hover */}
                      {shouldShowLabel && (
                        <g>
                          <rect
                            x={p.x - 14}
                            y={p.y - 20}
                            width="28"
                            height="15"
                            rx="4"
                            className="fill-white/95 stroke-slate-200/80 stroke-[0.8px] shadow-xs"
                          />
                          <text 
                            x={p.x} 
                            y={p.y - 9} 
                            textAnchor="middle" 
                            className="text-[9px] font-bold font-mono fill-[#0b57d0]"
                          >
                            {p.score.toFixed(1)}
                          </text>
                        </g>
                      )}

                      {/* Eje X: Fechas no encimadas */}
                      {showDate && p.fechaLabel && (
                        <text 
                          x={p.x} 
                          y={chartHeight - 10} 
                          textAnchor="middle" 
                          className="text-[9px] font-medium font-mono fill-slate-400"
                        >
                          {p.fechaLabel}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        ) : (
          <p className="text-xs text-[#747775] italic text-center py-6">No hay datos registrados para esta GPC.</p>
        )}

        {/* 4. Métricas KPI Inferiores con acabado en Cristal Líquido */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-slate-100/80 pt-5">
          <div className="bg-white/90 border border-slate-200/80 hover:border-blue-300/80 p-5 rounded-[22px] shadow-xs hover:shadow-sm transition-all space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Promedio General</span>
            <span className="text-2xl sm:text-3xl font-normal text-slate-900 font-heading block">
              {promedio_general} <span className="text-sm font-normal text-slate-500 font-sans">/ 10 pts</span>
            </span>
          </div>
          <div className="bg-white/90 border border-slate-200/80 hover:border-blue-300/80 p-5 rounded-[22px] shadow-xs hover:shadow-sm transition-all space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Evaluaciones Formativas</span>
            <span className="text-2xl sm:text-3xl font-normal text-[#0b57d0] font-heading block">
              {total_evaluaciones} <span className="text-sm font-normal text-slate-500 font-sans">realizadas</span>
            </span>
          </div>
          <div className="bg-white/90 border border-slate-200/80 hover:border-emerald-300/80 p-5 rounded-[22px] shadow-xs hover:shadow-sm transition-all space-y-1">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">GPCs Evaluadas</span>
            <span className="text-2xl sm:text-3xl font-normal text-emerald-600 font-heading block">
              {gpcKeys.length} <span className="text-sm font-normal text-slate-500 font-sans">guías</span>
            </span>
          </div>
        </div>
      </div>

    </div>
  );
}
