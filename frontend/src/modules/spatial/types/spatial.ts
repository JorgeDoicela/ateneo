export type BedUrgency = 'codigo_rojo' | 'urgente' | 'moderado';

export interface BedVitals {
  hr: number;
  bp: string;
  rr: number;
  spo2: number;
  temp: number;
}

export interface BedSpatialData {
  id: string;
  bedNumber: number;
  label: string;
  position: [number, number, number];
  rotation: [number, number, number];
  caseId: string;
  urgency: BedUrgency;
  isSolved: boolean;
  score?: number;
  vitals: BedVitals;
}
