export type StudyPlanStatus = 'active' | 'completed' | 'expired';
export type StudyPlanTaskType = 'gpc_reading' | 'case_simulation' | 'socratic_review';

export interface StudyPlanTask {
  id?: number;
  plan_id: string;
  task_type: StudyPlanTaskType;
  title: string;
  description: string;
  resource_reference: string;
  competency_id: string;
  estimated_minutes: number;
  is_completed: boolean;
  completed_at?: string | null;
}

export interface PrescriptiveStudyPlan {
  id: string;
  user_id: string;
  source_assessment_id?: string | null;
  title: string;
  diagnosis_summary: string;
  target_duration_days: number;
  progress_percentage: number;
  status: StudyPlanStatus;
  created_at: string;
  completed_at?: string | null;
  tasks: StudyPlanTask[];
}

export interface CompleteTaskResponse {
  task_id: number;
  plan_id: string;
  is_completed: boolean;
  progress_percentage: number;
  plan_completed: boolean;
  completed_at: string;
}
