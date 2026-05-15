export interface DimensionScore {
  score: number;
  max: number;
  comment: string;
}

export interface QuestionReview {
  question: string;
  answer_summary: string;
  score: number;
  comment: string;
  improved_answer_suggestion: string;
}

export interface Report {
  id?: string;
  interview_id?: string;
  total_score: number;
  dimension_scores: Record<string, DimensionScore>;
  overall_comment: string;
  strengths: string[];
  weaknesses: string[];
  resume_risks: string[];
  question_reviews: QuestionReview[];
  next_training_plan: string[];
}
