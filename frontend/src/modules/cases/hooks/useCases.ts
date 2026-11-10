import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import casesApi from '../api/casesApi';
import analyticsApi from '../../analytics/api/analyticsApi';
import offlineDb from '../../../core/storage/offlineDb';
import { useClinicalCaseSessionStore } from '../../../core/stores/useClinicalCaseSessionStore';
import type { ClinicalCase } from '../../../types';

export interface GpcMeta {
  label: string;
  category: string;
  time: string;
  isUrgent: boolean;
}

export const GPC_LABELS: Record<string, GpcMeta> = {
  // Mapeo canónico por archivo PDF oficial
  'MSP_Trastornos-hipertensivos-del-embarazo-con-portada-3.pdf': { label: 'GPC Trastornos Hipertensivos del Embarazo', category: 'ginecologia', time: '12-15 min', isUrgent: true },
  'Guía-de-hemorragia-postparto.pdf': { label: 'GPC Hemorragia Posparto (Código Rojo)', category: 'ginecologia', time: '15-18 min', isUrgent: true },
  'GP_Tuberculosis-1.pdf': { label: 'GPC Tuberculosis Pulmonar', category: 'neumologia', time: '12-15 min', isUrgent: false },
  'gpc_VIH_acuerdo_ministerial05-07-2019.pdf': { label: 'GPC Manejo Integral de VIH (MSP)', category: 'urgencias', time: '10-14 min', isUrgent: false },
  'gpc_hta192019.pdf': { label: 'GPC Hipertensión Arterial Primaria', category: 'med_interna', time: '10-12 min', isUrgent: false },
  'guia_prevencion_diagnostico_tratamiento_enfermedad_renal_cronica_2018.pdf': { label: 'GPC Enfermedad Renal Crónica', category: 'nefrologia', time: '12-15 min', isUrgent: false },
  'gpc_ehirn2019.pdf': { label: 'GPC Encefalopatía Hipóxico-Isquémica (EHI-RN)', category: 'pediatria', time: '12-15 min', isUrgent: true },
  'GPC_neumonía-adquirida_2017.pdf': { label: 'GPC Neumonía Adquirida en Comunidad', category: 'neumologia', time: '12-15 min', isUrgent: false },
  'GPC-Sepsis-neonatal.pdf': { label: 'GPC Sepsis Neonatal', category: 'pediatria', time: '12-15 min', isUrgent: true },
  'gpc_guia_aborto_espontaneo_incompleto_19_feb_2014.pdf': { label: 'GPC Manejo del Aborto Incompleto', category: 'ginecologia', time: '10-14 min', isUrgent: true },

  // Alias y slugs históricos para retrocompatibilidad
  'preeclampsia': { label: 'GPC Trastornos Hipertensivos del Embarazo', category: 'ginecologia', time: '12-15 min', isUrgent: true },
  'hemorragia_posparto': { label: 'GPC Hemorragia Posparto (Código Rojo)', category: 'ginecologia', time: '15-18 min', isUrgent: true },
  'gp_tuberculosis-1': { label: 'GPC Tuberculosis Pulmonar', category: 'neumologia', time: '12-15 min', isUrgent: false },
  'gpc_vih_acuerdo_ministerial05-07-2019': { label: 'GPC Manejo Integral de VIH (MSP)', category: 'urgencias', time: '10-14 min', isUrgent: false },
  'gpc_hta192019': { label: 'GPC Hipertensión Arterial Primaria', category: 'med_interna', time: '10-12 min', isUrgent: false },
  'guia_prevencion_diagnostico_tratamiento_enfermedad_renal_cronica_2018': { label: 'GPC Enfermedad Renal Crónica', category: 'nefrologia', time: '12-15 min', isUrgent: false },
  'gpc_ehirn2019': { label: 'GPC Encefalopatía Hipóxico-Isquémica (EHI-RN)', category: 'pediatria', time: '12-15 min', isUrgent: true },
  'gpc-neumonia_adquirida_en_la_comunidad': { label: 'GPC Neumonía Adquirida en Comunidad', category: 'neumologia', time: '12-15 min', isUrgent: false },
  'neumonia': { label: 'GPC Neumonía Adquirida en Comunidad Pediátrica', category: 'pediatria', time: '10-14 min', isUrgent: true },
  'gpc-sepsis-neonatal': { label: 'GPC Sepsis Neonatal', category: 'pediatria', time: '12-15 min', isUrgent: true },
  'gpc_guia_aborto_espontaneo_incompleto_19_feb_2014': { label: 'GPC Manejo del Aborto Incompleto', category: 'ginecologia', time: '10-14 min', isUrgent: true },
};

export function resolveGpcMeta(guia?: string): GpcMeta {
  if (!guia) {
    return {
      category: 'med_interna',
      isUrgent: false,
      label: 'GPC General',
      time: '10-15 min',
    };
  }
  if (GPC_LABELS[guia]) {
    return GPC_LABELS[guia];
  }
  const cleanGuia = guia.toLowerCase().replace(/\.pdf$/i, '').trim();
  const matchedKey = Object.keys(GPC_LABELS).find((key) => {
    const cleanKey = key.toLowerCase().replace(/\.pdf$/i, '');
    return cleanKey === cleanGuia || cleanKey.includes(cleanGuia) || cleanGuia.includes(cleanKey);
  });
  if (matchedKey) {
    return GPC_LABELS[matchedKey];
  }
  return {
    category: 'med_interna',
    isUrgent: false,
    label: guia.replace(/\.pdf$/i, '').replace(/[-_]/g, ' '),
    time: '10-15 min',
  };
}

/**
 * Normaliza cadenas clínicas eliminando acentos/tildes, espacios redundantes y convirtiendo a minúsculas.
 */
export function normalizeSearchText(text: string): string {
  return (text || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim();
}

export interface CategoryOption {
  id: string;
  label: string;
}

export const CATEGORIES: CategoryOption[] = [
  { id: 'all', label: 'Todos los Casos' },
  { id: 'urgencias', label: 'Urgencias & Infectología' },
  { id: 'ginecologia', label: 'Gineco-Obstetricia' },
  { id: 'med_interna', label: 'Medicina Interna' },
  { id: 'neumologia', label: 'Neumología' },
  { id: 'pediatria', label: 'Pediatría & Neonatología' },
  { id: 'nefrologia', label: 'Nefrología' },
];

export type ViewMode = 'grid' | 'list';
export type ClassificationTab = 'all' | 'urgent';

export interface CaseProgressInfo {
  status: 'completed' | 'in_progress' | 'not_started';
  score?: number;
  currentPhase?: number;
  totalPhases?: number;
}

export interface ExtendedClinicalCase extends ClinicalCase {
  guia_asociada?: string;
  enunciado?: string;
  progress?: CaseProgressInfo;
}

/**
 * useCases — Hook controlador para el catálogo de casos clínicos
 * Potenciado con TanStack Query para caché instantánea y revalidación en segundo plano.
 */
export function useCases(searchQuery: string = '') {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [classificationTab, setClassificationTab] = useState<ClassificationTab>('all');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  const {
    data: rawCases = [],
    isLoading: loading,
    error: queryError,
    refetch: reloadCases,
  } = useQuery<ExtendedClinicalCase[], Error>({
    queryKey: ['clinical-cases'],
    queryFn: async () => {
      try {
        const data = await casesApi.getCases();
        const casesList = data as ExtendedClinicalCase[];
        await offlineDb.saveCases(casesList);
        return casesList;
      } catch (networkErr) {
        const localCases = await offlineDb.getAllCases();
        if (localCases && localCases.length > 0) {
          return localCases as ExtendedClinicalCase[];
        }
        throw networkErr;
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  const { data: userHistory = [] } = useQuery<Array<{ case_id: string; score: number }>>({
    queryKey: ['user-evaluation-history'],
    queryFn: async () => {
      try {
        const hist = await analyticsApi.getHistory();
        return Array.isArray(hist) ? (hist as Array<{ case_id: string; score: number }>) : [];
      } catch {
        return [];
      }
    },
    staleTime: 30 * 1000,
  });

  const localSessions = useClinicalCaseSessionStore((state) => state.sessions);

  const cases = useMemo(() => {
    const historyMap: Record<string, number> = {};
    for (const h of userHistory) {
      const cid = h.case_id || (h as any).caso_id;
      if (cid && typeof h.score === 'number') {
        historyMap[cid] = h.score;
      }
    }

    return rawCases.map((c) => {
      const localSess = localSessions[c.id];
      const hasHistoryScore = historyMap[c.id] !== undefined;

      let progress: CaseProgressInfo = { status: 'not_started' };

      if (hasHistoryScore || (localSess && localSess.isCompleted)) {
        const score = localSess?.finalResult?.score ?? historyMap[c.id] ?? 8.0;
        progress = {
          status: 'completed',
          score,
          totalPhases: c.fases?.length || 3,
        };
      } else if (
        localSess &&
        (localSess.completedPhases?.length > 0 || (localSess.activeDraft && localSess.activeDraft.trim().length > 0))
      ) {
        progress = {
          status: 'in_progress',
          currentPhase: localSess.currentPhase || 1,
          totalPhases: c.fases?.length || 3,
        };
      }

      return {
        ...c,
        progress,
      };
    });
  }, [rawCases, userHistory, localSessions]);

  const error = queryError ? queryError.message : null;

  const filteredCases = useMemo(() => {
    return cases.filter((c) => {
      const gpcMeta = resolveGpcMeta(c.guia_asociada);

      // Filtro por categoría
      if (selectedCategory !== 'all' && gpcMeta.category !== selectedCategory) {
        return false;
      }

      // Filtro por tab de urgencia
      if (classificationTab === 'urgent' && !gpcMeta.isUrgent) {
        return false;
      }

      // Filtro por búsqueda
      if (searchQuery.trim()) {
        const queryTerms = normalizeSearchText(searchQuery).split(/\s+/).filter(Boolean);
        const corpus = normalizeSearchText(
          `${c.titulo || ''} ${c.guia_asociada || ''} ${gpcMeta.label || ''} ${gpcMeta.category || ''} ${c.especialidad || ''} ${c.enunciado || c.caso_preambulo || ''} ${c.pregunta || ''} ${(c.competencias_activadas || []).join(' ')} ${c.dificultad || ''}`
        );
        return queryTerms.every((term) => corpus.includes(term));
      }

      return true;
    });
  }, [cases, selectedCategory, classificationTab, searchQuery]);

  return {
    cases,
    filteredCases,
    loading,
    error,
    selectedCategory,
    setSelectedCategory,
    classificationTab,
    setClassificationTab,
    viewMode,
    setViewMode,
    reloadCases,
    categories: CATEGORIES,
    gpcLabels: GPC_LABELS,
  };
}

export default useCases;
