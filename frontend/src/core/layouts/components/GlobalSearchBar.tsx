import { useState, useRef, useEffect, ChangeEvent, KeyboardEvent } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Search, 
  SlidersHorizontal, 
  X, 
  Zap, 
  Layers, 
  ArrowRight, 
  Filter, 
  TrendingUp, 
  Stethoscope, 
  CornerDownLeft 
} from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';
import casesApi from '../../../modules/cases/api/casesApi';
import { 
  normalizeSearchText, 
  resolveGpcMeta, 
  CATEGORIES, 
  ExtendedClinicalCase 
} from '../../../modules/cases/hooks/useCases';

export interface GlobalSearchBarProps {
  isMobile?: boolean;
  onClose?: () => void;
}

const SUGGESTED_SEARCHES = [
  { label: 'Hemorragia Posparto (Código Rojo)', query: 'hemorragia' },
  { label: 'Trastornos Hipertensivos / Preeclampsia', query: 'preeclampsia' },
  { label: 'Tuberculosis Pulmonar', query: 'tuberculosis' },
  { label: 'Sepsis Neonatal', query: 'sepsis' },
  { label: 'Manejo Integral de VIH', query: 'vih' },
];

/**
 * GlobalSearchBar — Spotlight Clínico Inteligente (Ateneo+)
 * Características de alta fidelidad:
 * - Normalización fonética y de acentos (búsqueda insensible a tildes).
 * - Menú flotante predictivo en vivo con previsualización clínica inmediata.
 * - Navegación integral por teclado (flechas arriba/abajo, Enter para abrir caso, Escape para cerrar).
 * - Atajo global de teclado (Ctrl + K o Cmd + K).
 * - Panel emergente de filtros avanzados clínicos (urgencia y especialidad).
 */
export default function GlobalSearchBar({ isMobile, onClose }: GlobalSearchBarProps) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams, setSearchParams] = useSearchParams();

  const [isOpen, setIsOpen] = useState(false);
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const isAuthRoute = ['/login', '/register', '/auth/magic-login', '/magic-login'].some(p => 
    location.pathname.startsWith(p)
  );

  // Consulta de casos en caché con TanStack Query
  const { data: rawCases = [] } = useQuery({
    queryKey: ['clinicalCases'],
    queryFn: casesApi.getCases,
    staleTime: 5 * 60 * 1000,
  });

  const cases = rawCases as ExtendedClinicalCase[];
  const searchQuery = searchParams.get('q') || '';

  // Atajo Global de Teclado (Ctrl + K o Cmd + K)
  useEffect(() => {
    function handleGlobalKeyDown(e: globalThis.KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
    }
    window.addEventListener('keydown', handleGlobalKeyDown);
    return () => window.removeEventListener('keydown', handleGlobalKeyDown);
  }, []);

  // Cierre al hacer clic fuera o presionar Escape
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setIsFilterPanelOpen(false);
      }
    }
    function handleKeyDown(e: globalThis.KeyboardEvent) {
      if (e.key === 'Escape') {
        setIsOpen(false);
        setIsFilterPanelOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  if (isAuthRoute || !user) {
    return null;
  }

  // Filtrado predictivo inteligente con normalización fonética y scoring
  const matchingCases = cases
    .map((c) => {
      if (!searchQuery.trim()) return { caso: c, score: 0 };
      const terms = normalizeSearchText(searchQuery).split(/\s+/).filter(Boolean);
      const gpcMeta = resolveGpcMeta(c.guia_asociada);
      
      const tituloNorm = normalizeSearchText(c.titulo || '');
      const guiaNorm = normalizeSearchText(c.guia_asociada || '');
      const gpcLabelNorm = normalizeSearchText(gpcMeta.label || '');
      const especialidadNorm = normalizeSearchText(c.especialidad || gpcMeta.category || '');
      const enunciadoNorm = normalizeSearchText(c.enunciado || c.caso_preambulo || '');
      const competenciasNorm = normalizeSearchText((c.competencias_activadas || []).join(' '));

      let score = 0;
      const allMatch = terms.every((term) => {
        let termMatches = false;
        if (tituloNorm.includes(term)) { score += 12; termMatches = true; }
        if (gpcLabelNorm.includes(term) || guiaNorm.includes(term)) { score += 8; termMatches = true; }
        if (especialidadNorm.includes(term)) { score += 6; termMatches = true; }
        if (competenciasNorm.includes(term)) { score += 5; termMatches = true; }
        if (enunciadoNorm.includes(term)) { score += 3; termMatches = true; }
        return termMatches;
      });

      return allMatch ? { caso: c, score } : null;
    })
    .filter((item): item is { caso: ExtendedClinicalCase; score: number } => item !== null)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map((item) => item.caso);

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setActiveIndex(-1);
    setIsOpen(true);

    if (location.pathname !== '/' && location.pathname !== '/cases') {
      navigate(`/?q=${encodeURIComponent(val)}`);
    } else {
      if (val) {
        setSearchParams((prev) => {
          const next = new URLSearchParams(prev);
          next.set('q', val);
          return next;
        });
      } else {
        setSearchParams((prev) => {
          const next = new URLSearchParams(prev);
          next.delete('q');
          return next;
        });
      }
    }
  };

  const handleSelectCase = (caseId: string) => {
    setIsOpen(false);
    setIsFilterPanelOpen(false);
    if (onClose) onClose();
    navigate(`/cases/${caseId}`);
  };

  const handleApplySuggestion = (suggestedQuery: string) => {
    setIsOpen(true);
    if (location.pathname !== '/' && location.pathname !== '/cases') {
      navigate(`/?q=${encodeURIComponent(suggestedQuery)}`);
    } else {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        next.set('q', suggestedQuery);
        return next;
      });
    }
    inputRef.current?.focus();
  };

  const handleClear = () => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      next.delete('q');
      return next;
    });
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen && (e.key === 'ArrowDown' || e.key === 'Enter')) {
      setIsOpen(true);
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => (prev < matchingCases.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : matchingCases.length - 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && matchingCases[activeIndex]) {
        handleSelectCase(matchingCases[activeIndex].id);
      } else if (matchingCases.length > 0) {
        handleSelectCase(matchingCases[0].id);
      } else {
        setIsOpen(false);
        if (location.pathname !== '/' && location.pathname !== '/cases') {
          navigate(`/?q=${encodeURIComponent(searchQuery)}`);
        }
      }
    }
  };

  return (
    <div 
      ref={containerRef}
      className={isMobile ? "relative w-full flex items-center" : "relative w-full max-w-2xl mx-auto hidden md:flex items-center"}
    >
      {/* Halo de Refracción Óptica Ambiental de Cristal Líquido */}
      <div 
        className={`absolute -inset-0.5 bg-gradient-to-r from-cyan-500/20 via-blue-500/15 to-indigo-500/20 rounded-full blur-md transition-opacity duration-300 pointer-events-none ${
          isOpen ? 'opacity-90' : 'opacity-40'
        }`}
        aria-hidden="true"
      />

      {/* 1. Cápsula de Búsqueda Liquid Glassmorphism */}
      <div 
        className={`relative w-full rounded-full px-3.5 sm:px-4 py-1.5 sm:py-2 transition-all duration-300 flex items-center gap-2.5 sm:gap-3 bg-white/75 hover:bg-white/90 backdrop-blur-xl border border-white/90 shadow-[0_4px_20px_-2px_rgba(15,23,42,0.06),inset_0_1px_2px_rgba(255,255,255,0.95)] ${
          isOpen 
            ? 'bg-white/95 shadow-[0_8px_30px_-4px_rgba(37,99,235,0.12),inset_0_1px_2px_rgba(255,255,255,1)] border-white' 
            : ''
        }`}
      >
        <Search className={`w-4 h-4 shrink-0 transition-colors ${isOpen ? 'text-[#0b57d0]' : 'text-slate-500'}`} />
        
        <input
          ref={inputRef}
          type="text"
          placeholder={isMobile ? "Buscar casos, síntomas o GPC..." : "Buscar en Ateneo: casos clínicos, síntomas, diagnósticos o GPC Ecuador..."}
          value={searchQuery}
          onChange={handleSearchChange}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          className="w-full bg-transparent text-xs sm:text-sm text-[#1f1f1f] focus:outline-none placeholder:text-[#747775]"
          autoFocus={isMobile}
        />


        {/* Botón de Limpiar Búsqueda */}
        {searchQuery && (
          <button
            type="button"
            onClick={handleClear}
            className="text-xs text-[#747775] hover:text-[#1f1f1f] p-1 rounded-full hover:bg-slate-200/60 transition-colors cursor-pointer shrink-0"
            title="Limpiar búsqueda"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}

        {/* Botón de Filtros Clínicos Avanzados */}
        <button
          type="button"
          title="Filtros Clínicos Avanzados"
          onClick={() => {
            setIsFilterPanelOpen(!isFilterPanelOpen);
            setIsOpen(false);
          }}
          className={`p-1.5 rounded-full transition-colors cursor-pointer shrink-0 ${
            isFilterPanelOpen 
              ? 'bg-blue-50 text-[#0b57d0]' 
              : 'text-[#747775] hover:text-[#1f1f1f] hover:bg-slate-100'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Menú Desplegable Spotlight Predictivo en Vivo */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-[24px] shadow-2xl border border-slate-200/80 py-3 z-50 animate-fadeIn max-h-[460px] overflow-y-auto divide-y divide-slate-100">
          {searchQuery.trim() ? (
            <div>
              <div className="px-4 py-1.5 flex items-center justify-between text-[11px] font-semibold text-[#747775] uppercase tracking-wider">
                <span>Resultados de Simulación Clínica ({matchingCases.length})</span>
                <span className="text-[10px] font-normal lowercase">Enter para abrir</span>
              </div>

              {matchingCases.length > 0 ? (
                <div className="py-1">
                  {matchingCases.map((c, idx) => {
                    const gpcMeta = resolveGpcMeta(c.guia_asociada);
                    const isUrgent = gpcMeta.isUrgent;
                    const isActive = idx === activeIndex;

                    return (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => handleSelectCase(c.id)}
                        onMouseEnter={() => setActiveIndex(idx)}
                        className={`w-full px-4 py-2.5 text-left flex items-start justify-between gap-3 transition-colors cursor-pointer ${
                          isActive ? 'bg-sky-50/80' : 'hover:bg-slate-50'
                        }`}
                      >
                        <div className="space-y-1 flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className={`text-[11px] font-semibold ${isUrgent ? 'text-rose-700' : 'text-[#0b57d0]'}`}>
                              {gpcMeta.label}
                            </span>
                            {isUrgent && (
                              <span className="inline-flex items-center gap-0.5 text-[10px] font-semibold text-rose-700 bg-rose-50 px-1.5 py-0.5 rounded-full">
                                <Zap className="w-2.5 h-2.5" />
                                Código Rojo
                              </span>
                            )}
                            {c.fases && (
                              <span className="inline-flex items-center gap-0.5 text-[10px] font-medium text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded-full">
                                <Layers className="w-2.5 h-2.5 text-[#0b57d0]" />
                                3 Fases
                              </span>
                            )}
                          </div>
                          <h4 className="text-xs sm:text-sm font-normal text-[#1f1f1f] truncate font-heading">
                            {c.titulo}
                          </h4>
                          <p className="text-[11px] text-[#747775] line-clamp-1 leading-relaxed">
                            {c.enunciado || c.caso_preambulo}
                          </p>
                        </div>

                        <div className="shrink-0 pt-1">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center transition-all ${
                            isActive ? 'bg-[#0b57d0] text-white shadow-xs' : 'bg-slate-100 text-slate-500'
                          }`}>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              ) : (
                <div className="px-5 py-6 text-center space-y-2">
                  <Stethoscope className="w-6 h-6 text-slate-400 mx-auto opacity-70" />
                  <p className="text-xs font-medium text-[#1f1f1f]">
                    Sin coincidencias para &ldquo;{searchQuery}&rdquo;
                  </p>
                  <p className="text-[11px] text-[#747775] max-w-sm mx-auto">
                    Prueba con síntomas cardinales (cefalea, hemorragia), guías GPC Ecuador (código rojo, preeclampsia) o especialidades.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="px-4 py-2 space-y-3">
              <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[#747775] uppercase tracking-wider">
                <TrendingUp className="w-3.5 h-3.5 text-[#0b57d0]" />
                <span>Búsquedas Frecuentes y Guías de Práctica Clínica (GPC Ecuador)</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {SUGGESTED_SEARCHES.map((item) => (
                  <button
                    key={item.query}
                    type="button"
                    onClick={() => handleApplySuggestion(item.query)}
                    className="px-3 py-1.5 rounded-full text-xs text-[#444746] bg-slate-100/80 hover:bg-sky-50 hover:text-[#0b57d0] transition-colors cursor-pointer border border-transparent hover:border-sky-200"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Pie del Spotlight con Atajos */}
          <div className="px-4 pt-2.5 pb-1 flex items-center justify-between text-[11px] text-[#747775]">
            <div className="flex items-center gap-3">
              <span className="hidden sm:inline-flex items-center gap-1">
                <kbd className="px-1 py-0.5 text-[9px] bg-slate-100 border border-slate-200 rounded">↑</kbd>
                <kbd className="px-1 py-0.5 text-[9px] bg-slate-100 border border-slate-200 rounded">↓</kbd>
                navegar
              </span>
              <span className="inline-flex items-center gap-1">
                <kbd className="px-1 py-0.5 text-[9px] bg-slate-100 border border-slate-200 rounded">
                  <CornerDownLeft className="w-2.5 h-2.5 inline" />
                </kbd>
                abrir caso
              </span>
              <span className="hidden sm:inline-flex items-center gap-1">
                <kbd className="px-1 py-0.5 text-[9px] bg-slate-100 border border-slate-200 rounded">esc</kbd>
                cerrar
              </span>
            </div>
            <button
              type="button"
              onClick={() => {
                setIsOpen(false);
                if (location.pathname !== '/' && location.pathname !== '/cases') {
                  navigate(`/?q=${encodeURIComponent(searchQuery)}`);
                }
              }}
              className="text-[#0b57d0] hover:underline font-medium cursor-pointer"
            >
              Ver en catálogo →
            </button>
          </div>
        </div>
      )}

      {/* 3. Panel Emergente de Filtros Clínicos Avanzados */}
      {isFilterPanelOpen && (
        <div className="absolute top-full right-0 mt-2 w-80 max-w-[calc(100vw-2rem)] bg-white rounded-[24px] shadow-2xl border border-slate-200/80 p-5 z-50 animate-fadeIn space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-[#0b57d0]" />
              <h4 className="text-xs font-semibold text-[#1f1f1f] font-heading">
                Filtros Rápidos de Casos
              </h4>
            </div>
            <button
              type="button"
              onClick={() => setIsFilterPanelOpen(false)}
              className="p-1 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-[11px] font-medium text-[#747775] mb-1.5">
                Especialidad Médica
              </label>
              <div className="grid grid-cols-2 gap-1.5 max-h-36 overflow-y-auto no-scrollbar">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    type="button"
                    onClick={() => {
                      setIsFilterPanelOpen(false);
                      navigate(`/?category=${cat.id}`);
                      if (onClose) onClose();
                    }}
                    className="px-2.5 py-1.5 rounded-[12px] text-[11px] text-left truncate bg-slate-50 hover:bg-sky-50 hover:text-[#0b57d0] text-slate-700 transition-colors cursor-pointer"
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-3 flex items-center justify-between">
              <button
                type="button"
                onClick={() => {
                  setIsFilterPanelOpen(false);
                  navigate('/?tab=urgent');
                  if (onClose) onClose();
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-rose-700 bg-rose-50 hover:bg-rose-100 transition-colors cursor-pointer"
              >
                <Zap className="w-3 h-3 text-rose-600" />
                Solo Código Rojo
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsFilterPanelOpen(false);
                  navigate('/');
                  if (onClose) onClose();
                }}
                className="text-[11px] text-slate-500 hover:text-slate-900 cursor-pointer"
              >
                Restablecer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
