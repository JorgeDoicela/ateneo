export type AssessmentType = 'pre_test' | 'post_test' | 'baseline';
export type AssessmentStatus = 'pending' | 'in_progress' | 'completed';

export interface DiagnosticItem {
  id?: number;
  assessment_id: string;
  case_id?: string | null;
  prompt_text: string;
  student_answer: string;
  score_obtained: number;
  omisiones_json: string;
  competencias_json: string;
}

export interface DiagnosticAssessment {
  id: string;
  user_id: string;
  assessment_type: AssessmentType;
  related_assessment_id?: string | null;
  specialty_scope: string;
  score_total: number;
  score_max: number;
  hake_gain_g?: number | null;
  status: AssessmentStatus;
  started_at: string;
  completed_at?: string | null;
  items: DiagnosticItem[];
}

export interface AssessmentSummaryReport {
  assessment_id: string;
  user_id: string;
  assessment_type: AssessmentType;
  score_total: number;
  score_max: number;
  hake_gain_g?: number | null;
  hake_category?: 'Ganancia Alta (g >= 0.70)' | 'Ganancia Media (0.30 <= g < 0.70)' | 'Ganancia Baja (g < 0.30)' | string | null;
  total_omisiones_detectadas: number;
  competencias_afectadas: string[];
  completed_at: string;
}

export interface IsomorphicCase {
  id: string;
  base_case_id: string;
  titulo: string;
  enunciado: string;
  pregunta: string;
  guia_asociada: string;
  competencias_evaluadas: string[];
  nivel_esperado: string;
  fragmento_gpc_ideal_id?: string | null;
  variaciones_isomorficas: Record<string, string>;
  faithfulness_score: number;
  justificacion_clinica: string;
  is_generated_by_llm: boolean;
}
