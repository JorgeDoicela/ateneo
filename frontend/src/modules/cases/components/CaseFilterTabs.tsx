import { useState, useRef, useEffect } from 'react';
import { LayoutGrid, List, Zap, Filter, ChevronDown, Check } from 'lucide-react';
import type { CategoryOption, ClassificationTab, ViewMode } from '../hooks/useCases';

export interface CaseFilterTabsProps {
  categories: CategoryOption[];
  selectedCategory: string;
  onSelectCategory: (id: string) => void;
  classificationTab: ClassificationTab;
  onSelectClassificationTab: (tab: ClassificationTab) => void;
  viewMode: ViewMode;
  onChangeViewMode: (mode: ViewMode) => void;
  totalCasesCount: number;
  filteredCount?: number;
}

/**
 * CaseFilterTabs — Barra de pestañas y categorías de casos
 * Móvil: Selector desplegable vertical intuitivo para evitar pérdida de opciones fuera de pantalla.
 * Escritorio: Fila de chips horizontales de acceso directo con un clic.
 */
export default function CaseFilterTabs({
  categories,
  selectedCategory,
  onSelectCategory,
  classificationTab,
  onSelectClassificationTab,
  viewMode,
  onChangeViewMode,
  totalCasesCount,
}: CaseFilterTabsProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeCategory = categories.find((c) => c.id === selectedCategory);
  const activeCategoryLabel = activeCategory ? activeCategory.label : 'Todos los Casos';

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsDropdownOpen(false);
      }
    }
    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isDropdownOpen]);

  return (
    <div data-tour="specialty-filters" className="space-y-4">
      {/* 1. Pestañas de Clasificación General y Selector de Vista */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-200/80">
        <div className="flex items-center gap-3 sm:gap-6 overflow-x-auto overflow-y-hidden no-scrollbar shrink min-w-0">
          <button
            type="button"
            onClick={() => onSelectClassificationTab('all')}
            className={`pb-2.5 pt-1 text-xs sm:text-sm font-medium whitespace-nowrap transition-colors cursor-pointer shrink-0 border-b-2 -mb-px ${
              classificationTab === 'all'
                ? 'border-[#0b57d0] text-[#0b57d0] font-semibold'
                : 'border-transparent text-[#444746] hover:text-[#1f1f1f]'
            }`}
          >
            <span>Todos los Casos ({totalCasesCount})</span>
          </button>

          <button
            type="button"
            onClick={() => onSelectClassificationTab('urgent')}
            className={`pb-2.5 pt-1 text-xs sm:text-sm font-medium flex items-center gap-1.5 whitespace-nowrap transition-colors cursor-pointer shrink-0 border-b-2 -mb-px ${
              classificationTab === 'urgent'
                ? 'border-rose-600 text-rose-700 font-semibold'
                : 'border-transparent text-[#444746] hover:text-[#1f1f1f]'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-rose-600 shrink-0" />
            <span>Código Rojo / Urgencias</span>
          </button>
        </div>

        {/* Selector de Vista (Grid vs List) */}
        <div className="flex items-center gap-1 bg-white/70 backdrop-blur-md p-1 rounded-full border border-slate-200/80 shadow-xs shrink-0 mb-1.5">
          <button
            onClick={() => onChangeViewMode('grid')}
            title="Vista en Cuadrícula"
            className={`p-1.5 rounded-full transition-all cursor-pointer ${
              viewMode === 'grid'
                ? 'bg-white shadow-xs text-blue-600 font-semibold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </button>
          <button
            onClick={() => onChangeViewMode('list')}
            title="Vista en Lista"
            className={`p-1.5 rounded-full transition-all cursor-pointer ${
              viewMode === 'list'
                ? 'bg-white shadow-xs text-blue-600 font-semibold'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            <List className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          </button>
        </div>
      </div>

      {/* 2. Selector Desplegable de Especialidades en Dispositivos Móviles (< sm) */}
      <div className="relative block sm:hidden" ref={dropdownRef}>
        <button
          type="button"
          onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          aria-expanded={isDropdownOpen}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-[18px] bg-white border border-slate-200/80 shadow-xs text-xs font-medium text-[#1f1f1f] hover:bg-slate-50 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-2 truncate pr-2">
            <Filter className="w-3.5 h-3.5 text-[#0b57d0] shrink-0" />
            <span className="text-[#747775] shrink-0">Especialidad:</span>
            <span className="font-semibold text-[#0b57d0] truncate">{activeCategoryLabel}</span>
          </div>
          <ChevronDown
            className={`w-4 h-4 text-[#747775] shrink-0 transition-transform duration-200 ${
              isDropdownOpen ? 'rotate-180 text-[#0b57d0]' : ''
            }`}
          />
        </button>

        {isDropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-[22px] shadow-xl border border-slate-100 py-2 z-30 animate-fadeIn max-h-72 overflow-y-auto">
            {categories.map((cat) => {
              const isSelected = selectedCategory === cat.id;
              return (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => {
                    onSelectCategory(cat.id);
                    setIsDropdownOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-xs text-left transition-colors cursor-pointer ${
                    isSelected
                      ? 'bg-blue-50/80 text-[#0b57d0] font-semibold'
                      : 'text-[#444746] hover:bg-slate-50 hover:text-[#1f1f1f]'
                  }`}
                >
                  <span className="truncate pr-2">{cat.label}</span>
                  {isSelected && <Check className="w-4 h-4 text-[#0b57d0] shrink-0" />}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 3. Chips de Especialidades Médicas en Escritorio (>= sm) */}
      <div className="hidden sm:flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar touch-pan-x">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => onSelectCategory(cat.id)}
            className={`px-3 sm:px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all duration-200 cursor-pointer ${
              selectedCategory === cat.id
                ? 'bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-600 text-white shadow-sm shadow-blue-500/25 font-semibold'
                : 'bg-white/90 backdrop-blur-xs text-slate-700 border border-slate-200/80 hover:bg-white hover:border-slate-300 hover:text-slate-900'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>
    </div>
  );
}
