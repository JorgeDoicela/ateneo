import type { AxisCompetencyItem } from '../../../types';

export interface SkillRadarChartProps {
  competenciasPorEje?: AxisCompetencyItem[];
}

interface AxisConfig {
  key: string;
  label: string;
  angle: number;
  align: 'middle' | 'start' | 'end';
}

export default function SkillRadarChart({ competenciasPorEje = [] }: SkillRadarChartProps) {
  const centerX = 190;
  const centerY = 150;
  const radius = 80;

  const axesConfig: AxisConfig[] = [
    { key: 'diagnóstico', label: 'Diagnóstico', angle: -Math.PI / 2, align: 'middle' },
    { key: 'tratamiento', label: 'Tratamiento', angle: 0, align: 'start' },
    { key: 'seguimiento', label: 'Seguimiento', angle: Math.PI / 2, align: 'middle' },
    { key: 'prevención', label: 'Prevención', angle: Math.PI, align: 'end' },
  ];

  const scoresByAxis = axesConfig.map(axis => {
    const matched = competenciasPorEje.find(e => {
      const eKey = (e.key || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
      const aKey = axis.key.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
      return eKey.includes(aKey);
    });

    if (matched) {
      if (typeof matched.score === 'number') {
        return Math.max(0, Math.min(100, matched.score));
      }
      const brechasCount = matched.items ? matched.items.length : 0;
      if (brechasCount === 0) return 95;
      if (brechasCount === 1) return 65;
      return 35;
    }
    return 85;
  });

  const levels = [0.25, 0.50, 0.75, 1.0];
  const gridPolygons = levels.map(level => {
    return axesConfig.map(axis => {
      const r = radius * level;
      const x = centerX + r * Math.cos(axis.angle);
      const y = centerY + r * Math.sin(axis.angle);
      return `${x},${y}`;
    }).join(' ');
  });

  const dataPoints = axesConfig.map((axis, i) => {
    const pct = scoresByAxis[i] / 100;
    const r = radius * pct;
    const x = centerX + r * Math.cos(axis.angle);
    const y = centerY + r * Math.sin(axis.angle);
    return { x, y, score: scoresByAxis[i], axis };
  });

  const polygonPath = dataPoints.map(p => `${p.x},${p.y}`).join(' ');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <h3 className="text-xl font-normal text-[#1f1f1f] font-heading">
            Radar de Competencias Clínicas (4 Ejes GPC)
          </h3>
          <p className="text-xs text-[#747775] mt-0.5">
            Consistencia diagnóstica y terapéutica frente a las Guías de Práctica Clínica (GPC Ecuador)
          </p>
        </div>
        <span className="text-xs font-semibold bg-gradient-to-r from-cyan-50/70 via-blue-50/50 to-indigo-50/70 border border-blue-200/60 text-[#0b57d0] px-3.5 py-1 rounded-full shadow-2xs">
          Analítica 4 Ejes
        </span>
      </div>

      <div className="flex flex-col lg:flex-row items-center justify-between gap-8 pt-2">
        <div className="w-full lg:w-1/2 max-w-[380px] relative flex items-center justify-center">
          <svg viewBox="0 0 380 300" className="w-full h-auto overflow-visible">
            <defs>
              <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.30" />
                <stop offset="100%" stopColor="#2563eb" stopOpacity="0.15" />
              </linearGradient>
            </defs>

            {/* Ejes Radiales */}
            {axesConfig.map((axis, idx) => {
              const xEnd = centerX + radius * Math.cos(axis.angle);
              const yEnd = centerY + radius * Math.sin(axis.angle);
              return (
                <line
                  key={idx}
                  x1={centerX}
                  y1={centerY}
                  x2={xEnd}
                  y2={yEnd}
                  stroke="#cbd5e1"
                  strokeWidth="1.2"
                  strokeDasharray="2 3"
                />
              );
            })}

            {/* Anillos Poligonales de Nivel */}
            {gridPolygons.map((polyStr, idx) => (
              <polygon
                key={idx}
                points={polyStr}
                fill="none"
                stroke="#e2e8f0"
                strokeWidth={idx === gridPolygons.length - 1 ? 1.5 : 1}
              />
            ))}

            {/* Polígono de Desempeño */}
            <polygon
              points={polygonPath}
              fill="url(#radarGradient)"
              stroke="#2563eb"
              strokeWidth="2.5"
              className="transition-all duration-700 ease-out"
            />

            {/* Puntos en los Vértices */}
            {dataPoints.map((p, idx) => (
              <g key={idx} className="group">
                <circle
                  cx={p.x}
                  cy={p.y}
                  r="5"
                  fill="#0b57d0"
                  stroke="#ffffff"
                  strokeWidth="2.5"
                  className="shadow-sm"
                />
              </g>
            ))}

            {/* Etiquetas de los Ejes Holgadas y sin Recortes */}
            {axesConfig.map((axis, idx) => {
              const rLabel = radius + (axis.key === 'diagnóstico' ? 18 : axis.key === 'seguimiento' ? 22 : 16);
              const lx = centerX + rLabel * Math.cos(axis.angle);
              const ly = centerY + rLabel * Math.sin(axis.angle) + (axis.key === 'tratamiento' || axis.key === 'prevención' ? 4 : 0);
              const score = scoresByAxis[idx];

              return (
                <text
                  key={idx}
                  x={lx}
                  y={ly}
                  textAnchor={axis.align}
                  className="fill-[#1f1f1f] text-[11px] font-semibold select-none font-sans"
                >
                  {axis.label} ({score}%)
                </text>
              );
            })}
          </svg>
        </div>

        {/* Panel Derecho: Barras de Dominio en Cristal Líquido */}
        <div className="w-full lg:w-1/2 space-y-3">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            <span>Nivel de Dominio por Eje Clínico</span>
          </div>

          <div className="space-y-2.5">
            {axesConfig.map((axis, idx) => {
              const score = scoresByAxis[idx];
              const matched = competenciasPorEje.find(e => {
                const eKey = (e.key || '').normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
                const aKey = axis.key.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
                return eKey.includes(aKey);
              });

              let barColor = 'bg-gradient-to-r from-blue-500 to-indigo-600';
              let badgeText = matched?.estadoLabel || 'Alto';
              let badgeBg = 'bg-sky-50 text-[#0b57d0] border-sky-200/70';

              if (score === 0) {
                barColor = 'bg-slate-300';
                badgeText = matched?.estadoLabel || 'No Demostrado';
                badgeBg = 'bg-slate-50 text-slate-600 border-slate-200/70';
              } else if (score < 50) {
                barColor = 'bg-gradient-to-r from-rose-500 to-pink-600';
                badgeText = matched?.estadoLabel || 'Brecha Crítica';
                badgeBg = 'bg-rose-50/90 text-rose-800 border-rose-200/70';
              } else if (score < 80) {
                barColor = 'bg-gradient-to-r from-amber-400 to-orange-500';
                badgeText = matched?.estadoLabel || 'En Desarrollo';
                badgeBg = 'bg-amber-50/90 text-amber-800 border-amber-200/70';
              } else {
                badgeText = matched?.estadoLabel || 'Consolidado';
                badgeBg = 'bg-emerald-50/90 text-emerald-800 border-emerald-200/70';
                barColor = 'bg-gradient-to-r from-emerald-500 to-teal-600';
              }

              return (
                <div key={axis.key} className="bg-white/85 hover:bg-white border border-slate-200/80 hover:border-blue-300/80 p-3.5 rounded-[18px] space-y-2 min-w-0 shadow-2xs transition-all">
                  <div className="flex flex-wrap items-center justify-between gap-1.5 text-xs font-medium min-w-0">
                    <span className="text-slate-800 font-semibold truncate">{axis.label}</span>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className={`text-[11px] font-medium px-2.5 py-0.5 rounded-full border ${badgeBg}`}>
                        {badgeText}
                      </span>
                      <span className="font-mono font-bold text-[#0b57d0]">{score}%</span>
                    </div>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${barColor}`}
                      style={{ width: `${score}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
