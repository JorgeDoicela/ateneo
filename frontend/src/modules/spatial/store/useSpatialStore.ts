import { create } from 'zustand';
import type { ClinicalCase } from '../../../types';
import type { BedSpatialData } from '../types/spatial';

export interface TouchInputState {
  moveX: number; // -1 (izq) a 1 (der)
  moveY: number; // -1 (atrás) a 1 (adelante)
  isSprinting: boolean;
  lookDeltaX: number;
  lookDeltaY: number;
}

interface SpatialState {
  playerPosition: [number, number, number];
  playerRotation: number;
  beds: BedSpatialData[];
  hoveredBedId: string | null;
  activeBedId: string | null;
  isTabletOpen: boolean;
  selectedCase: ClinicalCase | null;
  touchInput: TouchInputState;

  setPlayerTransform: (pos: [number, number, number], rot: number) => void;
  setHoveredBed: (bedId: string | null) => void;
  openBedInspection: (bedId: string) => void;
  closeBedInspection: () => void;
  syncCasesWithBeds: (cases: ClinicalCase[]) => void;
  markBedAsSolved: (caseId: string, score: number) => void;
  setTouchMove: (x: number, y: number) => void;
  setTouchSprinting: (sprinting: boolean) => void;
  addTouchLookDelta: (dx: number, dy: number) => void;
  consumeTouchLookDelta: () => { dx: number; dy: number };
}

const INITIAL_BEDS: BedSpatialData[] = [
  {
    id: 'bed_01',
    bedNumber: 1,
    label: 'Box de Choque 1 — Obstetricia',
    position: [-7, 0, -5.2],
    rotation: [0, 0, 0],
    caseId: 'case_preeclampsia_01',
    urgency: 'codigo_rojo',
    isSolved: false,
    vitals: { hr: 88, bp: '165/110', rr: 20, spo2: 97, temp: 36.8 }
  },
  {
    id: 'bed_02',
    bedNumber: 2,
    label: 'Box de Choque 2 — Código Rojo',
    position: [-7, 0, 5.2],
    rotation: [0, Math.PI, 0],
    caseId: 'case_hemorragia_01',
    urgency: 'codigo_rojo',
    isSolved: false,
    vitals: { hr: 125, bp: '85/50', rr: 26, spo2: 94, temp: 35.9 }
  },
  {
    id: 'bed_03',
    bedNumber: 3,
    label: 'Cama 3 — Aislamiento Respiratorio',
    position: [0, 0, -5.2],
    rotation: [0, 0, 0],
    caseId: 'case_tb_01',
    urgency: 'urgente',
    isSolved: false,
    vitals: { hr: 92, bp: '115/75', rr: 24, spo2: 92, temp: 38.4 }
  },
  {
    id: 'bed_04',
    bedNumber: 4,
    label: 'Cama 4 — Medicina Interna',
    position: [0, 0, 5.2],
    rotation: [0, Math.PI, 0],
    caseId: 'case_hta_01',
    urgency: 'moderado',
    isSolved: false,
    vitals: { hr: 78, bp: '170/105', rr: 16, spo2: 98, temp: 36.6 }
  },
  {
    id: 'bed_05',
    bedNumber: 5,
    label: 'Cama 5 — Nefrología',
    position: [7, 0, -5.2],
    rotation: [0, 0, 0],
    caseId: 'case_erc_01',
    urgency: 'moderado',
    isSolved: false,
    vitals: { hr: 84, bp: '155/95', rr: 18, spo2: 96, temp: 36.7 }
  },
  {
    id: 'bed_06',
    bedNumber: 6,
    label: 'Cama 6 — Pediatría / Observación',
    position: [7, 0, 5.2],
    rotation: [0, Math.PI, 0],
    caseId: 'case_nac_01',
    urgency: 'urgente',
    isSolved: false,
    vitals: { hr: 138, bp: '95/60', rr: 38, spo2: 90, temp: 39.1 }
  }
];

export const useSpatialStore = create<SpatialState>((set, get) => ({
  playerPosition: [-33.5, 1.62, 0],
  playerRotation: -Math.PI / 2,
  beds: INITIAL_BEDS,
  hoveredBedId: null,
  activeBedId: null,
  isTabletOpen: false,
  selectedCase: null,
  touchInput: {
    moveX: 0,
    moveY: 0,
    isSprinting: false,
    lookDeltaX: 0,
    lookDeltaY: 0
  },

  setPlayerTransform: (pos, rot) =>
    set({ playerPosition: pos, playerRotation: rot }),

  setHoveredBed: (bedId) =>
    set({ hoveredBedId: bedId }),

  setTouchMove: (x, y) =>
    set((state) => ({
      touchInput: { ...state.touchInput, moveX: x, moveY: y }
    })),

  setTouchSprinting: (sprinting) =>
    set((state) => ({
      touchInput: { ...state.touchInput, isSprinting: sprinting }
    })),

  addTouchLookDelta: (dx, dy) => {
    const current = get().touchInput;
    current.lookDeltaX += dx;
    current.lookDeltaY += dy;
  },

  consumeTouchLookDelta: () => {
    const current = get().touchInput;
    const dx = current.lookDeltaX;
    const dy = current.lookDeltaY;
    current.lookDeltaX = 0;
    current.lookDeltaY = 0;
    return { dx, dy };
  },

  openBedInspection: (bedId) => {
    const targetBed = get().beds.find((b) => b.id === bedId);
    if (!targetBed) return;
    set({
      activeBedId: bedId,
      isTabletOpen: true
    });
  },

  closeBedInspection: () =>
    set({
      isTabletOpen: false,
      activeBedId: null
    }),

  syncCasesWithBeds: (cases) => {
    if (!cases || cases.length === 0) return;
    set((state) => ({
      beds: state.beds.map((b) => {
        const matchingCase = cases.find((c) => c.id === b.caseId);
        if (!matchingCase) return b;
        return {
          ...b,
          label: matchingCase.titulo,
          urgency: matchingCase.signos_alarma || matchingCase.id.includes('hemorragia') || matchingCase.id.includes('preeclampsia')
            ? 'codigo_rojo'
            : matchingCase.dificultad === 'Avanzado'
            ? 'urgente'
            : 'moderado'
        };
      })
    }));
  },

  markBedAsSolved: (caseId, score) =>
    set((state) => ({
      beds: state.beds.map((b) =>
        b.caseId === caseId ? { ...b, isSolved: true, score } : b
      )
    }))
}));
