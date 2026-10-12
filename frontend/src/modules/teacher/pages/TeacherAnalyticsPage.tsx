import React from 'react';
import CoordinatorAnalytics from '../../analytics/components/CoordinatorAnalytics';

/**
 * Vista Dedicada: Analítica de Cohorte y Brechas Clínicas para Docentes (Ateneo+)
 * Integra indicadores psicométricos, Índice de Brecha Formativa (IBF) y alineación con GPC MSP.
 */
export const TeacherAnalyticsPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <CoordinatorAnalytics />
    </div>
  );
};

export default TeacherAnalyticsPage;
