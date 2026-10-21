import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Stethoscope, 
  AlertCircle 
} from 'lucide-react';
import useCases, { resolveGpcMeta } from '../hooks/useCases';
import CaseCard from '../components/CaseCard';
import CaseFilterTabs from '../components/CaseFilterTabs';
import DiagnosticPreTestBanner from '../components/DiagnosticPreTestBanner';
import AdaptiveNextCase from '../../adaptive/components/AdaptiveNextCase';
import KnowledgeSpaceGraph from '../../adaptive/components/KnowledgeSpaceGraph';
import { TourHelpButton, StudentTourGuide } from '../../../core/tour';

export default function CaseList() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const globalSearchQuery = searchParams.get('q') || '';
  const {
    filteredCases,
    cases,
    loading,
    error,
    selectedCategory,
    setSelectedCategory,
    classificationTab,
    setClassificationTab,
    viewMode,
    setViewMode,
    categories,
  } = useCases(globalSearchQuery);

  const [showKstGraph, setShowKstGraph] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' as ScrollBehavior });
    }
  }, [selectedCategory, classificationTab]);

  return (
    <div className="space-y-8 animate-fadeIn pb-36 sm:pb-24">
      
      {/* 1. Header Principal */}
      <div className="pb-2 pt-2">
        <h1 className="text-[28px] sm:text-[34px] font-normal tracking-tight text-[#1f1f1f] font-heading">
          Casos de Simulación Clínica
        </h1>
        <p className="text-sm font-normal text-[#444746] mt-1 max-w-2xl leading-relaxed">
          Casos estructurados según Guías de Práctica Clínica (GPC Ecuador) para la evaluación formativa del razonamiento clínico.
        </p>
      </div>

      {/* 2. Banner de Integración Formativa: Pre-Test CACES / Plan Prescriptivo Activo */}
      <DiagnosticPreTestBanner />

      {/* 3. Motor Adaptativo ZDP (KST + BKT) */}
      <AdaptiveNextCase
        onSelectCase={(clinicalCase) => navigate(`/cases/${clinicalCase.id}`)}
        onToggleGraph={() => setShowKstGraph(true)}
      />

          {/* 4. Barra de Filtros, Categorías y Pestañas */}
          <CaseFilterTabs
            categories={categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
            classificationTab={classificationTab}
            onSelectClassificationTab={setClassificationTab}
            viewMode={viewMode}
            onChangeViewMode={setViewMode}
            totalCasesCount={cases.length}
            filteredCount={filteredCases.length}
          />

          {/* 5. Estado de Carga o Error */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-4">
              {[1, 2, 3, 4, 5, 6].map((n) => (
                <div key={n} className="bg-white rounded-[28px] p-6 shadow-xs border-0 animate-pulse space-y-4">
                  <div className="h-4 bg-slate-200 rounded w-1/3"></div>
                  <div className="h-6 bg-slate-200 rounded w-4/5"></div>
                  <div className="h-16 bg-slate-100 rounded w-full"></div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="bg-rose-50 border border-rose-200 rounded-[24px] p-8 text-center space-y-3">
              <AlertCircle className="w-8 h-8 text-rose-600 mx-auto" />
              <p className="text-sm font-medium text-rose-900">{error}</p>
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="bg-white rounded-[28px] p-12 text-center shadow-xs border-0 space-y-3">
              <Stethoscope className="w-8 h-8 text-[#747775] mx-auto opacity-60" />
              <p className="text-base font-normal text-[#1f1f1f]">No se encontraron casos clínicos con ese criterio.</p>
              <p className="text-xs text-[#747775]">Prueba seleccionando otra especialidad o limpiando los términos de búsqueda.</p>
            </div>
          ) : (
            /* 6. Listado de Casos Clínicos (Grid o Lista) */
            <div
              className={
                viewMode === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2'
                  : 'space-y-4 pt-2'
              }
            >
              {filteredCases.map((caso, index) => (
                <div key={caso.id} {...(index === 0 ? { 'data-tour': 'case-card' } : {})}>
                  <CaseCard
                    caso={caso}
                    gpcMeta={resolveGpcMeta(caso.guia_asociada)}
                    viewMode={viewMode}
                  />
                </div>
              ))}
            </div>
          )}

      {/* Modal: Grafo de Espacio de Conocimiento (KST) */}
      <KnowledgeSpaceGraph
        isOpen={showKstGraph}
        onClose={() => setShowKstGraph(false)}
      />

      {/* Botón Flotante de Ayuda y Tour Guiado Formativo */}
      <TourHelpButton />
      <StudentTourGuide />
    </div>
  );
}
