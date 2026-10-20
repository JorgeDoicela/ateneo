import React from 'react';
import { TrendingUp, AlertTriangle, CheckCircle, ArrowDownRight } from 'lucide-react';

interface HakeGainBadgeProps {
  gain: number | null | undefined;
  category?: string | null;
  showDetails?: boolean;
}

export const HakeGainBadge: React.FC<HakeGainBadgeProps> = ({
  gain,
  category,
  showDetails = true,
}) => {
  if (gain === null || gain === undefined) {
    return (
      <span className="text-xs font-medium text-slate-400">
        Sin Post-Test vinculado
      </span>
    );
  }

  const g = Number(gain);

  // Clasificación psicométrica de Hake (1998)
  let label = 'Ganancia Baja';
  let textColor = 'text-amber-700';
  let IconComponent = AlertTriangle;

  if (g >= 0.70) {
    label = 'Ganancia Alta';
    textColor = 'text-emerald-700';
    IconComponent = CheckCircle;
  } else if (g >= 0.30) {
    label = 'Ganancia Media';
    textColor = 'text-blue-700';
    IconComponent = TrendingUp;
  } else if (g < 0.0) {
    label = 'Regresión Clínica';
    textColor = 'text-rose-700';
    IconComponent = ArrowDownRight;
  }

  const categoryLabel = category || label;

  return (
    <div className="inline-flex items-center gap-1.5 text-xs font-semibold">
      <IconComponent className={`w-3.5 h-3.5 ${textColor} shrink-0`} />
      <span className={textColor}>
        g = {g.toFixed(2)}
      </span>
      {showDetails && (
        <span className="text-slate-500 font-normal">
          • {categoryLabel}
        </span>
      )}
    </div>
  );
};
