export interface ExperienceInsight {
  id: string;
  experience_id: string;
  user_id: string;
  provider: string;
  model?: string | null;
  fallback_used: boolean;
  fallback_reason?: string | null;
  interview_process_json: string[];
  question_categories_json: Array<{ category: string; frequency: string; questions: string[] }>;
  real_questions_json: Array<{ question: string; category?: string | null; difficulty?: string | null; source_context?: string | null }>;
  focus_points_json: string[];
  risk_points_json: Array<{ level: string; point: string; suggestion?: string | null }>;
  suggested_strategy_json: string[];
  timeline_json: Array<{ step: string; estimated_minutes?: number | null; notes?: string | null }>;
  raw_result_json: Record<string, unknown>;
  created_at: string;
}

export interface ExperienceListItem {
  id: string;
  title: string;
  source_type: string;
  source_url?: string | null;
  source_site?: string | null;
  target_school?: string | null;
  target_major?: string | null;
  target_lab?: string | null;
  target_teacher?: string | null;
  interview_type?: string | null;
  year?: number | null;
  summary?: string | null;
  extract_status: 'pending' | 'success' | 'failed';
  extract_error?: string | null;
  real_question_count: number;
  focus_preview: string[];
  high_risk_preview: string[];
  created_at: string;
  updated_at: string;
}

export interface ExperienceDetail extends ExperienceListItem {
  raw_content: string;
  latest_insight?: ExperienceInsight | null;
}

export interface ExperienceImportPayload {
  title: string;
  source_url?: string | null;
  target_school?: string | null;
  target_major?: string | null;
  target_lab?: string | null;
  target_teacher?: string | null;
  interview_type?: string | null;
  year?: number | null;
  raw_content: string;
  llm_config_id?: string | null;
}

export interface ExperienceImportWebPayload {
  title: string;
  source_url: string;
  source_site?: string | null;
  snippet?: string | null;
  raw_content: string;
  target_school?: string | null;
  target_major?: string | null;
  target_lab?: string | null;
  target_teacher?: string | null;
  interview_type?: string | null;
  year?: number | null;
  llm_config_id?: string | null;
}

export interface ExperienceSearchPayload {
  keyword?: string;
  target_school?: string;
  target_major?: string;
  target_lab?: string;
  target_teacher?: string;
  interview_type?: string;
  year?: number;
  max_results?: number;
}

export interface ExperienceSearchResultItem {
  title: string;
  url: string;
  source_site?: string | null;
  snippet: string;
  raw_content: string;
  published_date?: string | null;
  score?: number | null;
}

export interface ExperienceSearchResponse {
  provider: string;
  query_used: string;
  message?: string | null;
  results: ExperienceSearchResultItem[];
}

export interface ExperienceUpdatePayload {
  title?: string;
  source_url?: string | null;
  target_school?: string | null;
  target_major?: string | null;
  target_lab?: string | null;
  target_teacher?: string | null;
  interview_type?: string | null;
  year?: number | null;
  raw_content?: string;
}
