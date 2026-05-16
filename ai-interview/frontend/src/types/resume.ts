export interface Resume {
  id: string;
  title: string;
  original_filename: string;
  file_size: number;
  content_type?: string | null;
  parse_status: string;
  parse_error?: string | null;
  analysis_status: 'none' | 'success' | 'failed' | 'outdated';
  latest_overall_score?: number | null;
  high_risks: string[];
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends Resume {
  parsed_text: string;
}

export interface ResumeSuggestion {
  priority: string;
  problem: string;
  advice: string;
  example?: string | null;
}

export interface ResumeSectionReview {
  section: string;
  score: number;
  comment: string;
}

export interface ResumeDiagnostic {
  id: string;
  resume_id: string;
  provider: string;
  model?: string | null;
  fallback_used: boolean;
  fallback_reason?: string | null;
  overall_score: number;
  summary: string;
  strengths_json: string[];
  weaknesses_json: string[];
  suggestions_json: ResumeSuggestion[];
  section_reviews_json: ResumeSectionReview[];
  follow_up_questions_json: string[];
  likely_interview_questions?: string[];
  raw_result_json: Record<string, unknown>;
  created_at: string;
}
