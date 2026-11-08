import React from 'react';
import { Html } from '@react-three/drei';
import { Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';
import type { BedSpatialData } from '../types/spatial';

interface BedInteractionBadgeProps {
  bed: BedSpatialData;
  isHovered?: boolean;
  onClick: () => void;
}

export const BedInteractionBadge: React.FC<BedInteractionBadgeProps> = ({
  bed,
  isHovered = false,
  onClick
}) => {
  return (
    <group position={[bed.position[0], 1.42, bed.position[2]]}>
      <Html
        center
        distanceFactor={8}
        zIndexRange={[10, 0]}
        className="pointer-events-auto select-none"
      >
        <button
          onClick={onClick}
          aria-label={`Examinar Cama ${bed.bedNumber}`}
          title={`Cama ${bed.bedNumber}: ${bed.label}`}
          className={`flex flex-col items-center backdrop-blur-md rounded-[16px] border shadow-md transition-all duration-200 cursor-pointer group ${
            isHovered
              ? 'bg-white/95 border-blue-400 px-3 py-1.5 scale-105 shadow-blue-500/15'
              : 'bg-white/90 hover:bg-white/95 border-slate-200/90 px-2.5 py-1'
          }`}
        >
          <div className="flex items-center space-x-1.5 text-slate-900 whitespace-nowrap">
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                bed.isSolved
                  ? 'bg-emerald-500'
                  : bed.urgency === 'codigo_rojo'
                  ? 'bg-red-500 animate-ping'
                  : 'bg-cyan-500'
              }`}
            />
            <span className="text-[11px] font-bold tracking-tight">
              Cama {bed.bedNumber}
            </span>
            {isHovered && (
              <span className="text-[10px] text-slate-600 font-medium max-w-[180px] truncate">
                • {bed.label}
              </span>
            )}
          </div>

          <div className="mt-0.5 flex items-center space-x-1 whitespace-nowrap">
            {bed.isSolved ? (
              <span className="inline-flex items-center text-[9px] font-semibold text-emerald-700">
                <CheckCircle2 className="w-2.5 h-2.5 inline mr-0.5" />
                Resuelto ({bed.score || 9.0}/10)
              </span>
            ) : bed.urgency === 'codigo_rojo' ? (
              <span className="inline-flex items-center text-[9px] font-bold text-red-600">
                <ShieldAlert className="w-2.5 h-2.5 inline mr-0.5" />
                CÓDIGO ROJO
              </span>
            ) : (
              <span className="inline-flex items-center text-[9px] font-medium text-[#0b57d0]">
                <Activity className="w-2.5 h-2.5 inline mr-0.5" />
                En Evaluación
              </span>
            )}
          </div>
        </button>
      </Html>
    </group>
  );
};

export default BedInteractionBadge;
