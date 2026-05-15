export type InterviewRole = 'interviewer' | 'candidate';

export interface InterviewConfig {
  type: string;
  interviewer_style: string;
  target_school?: string | null;
  target_major?: string | null;
  resume_text: string;
}

export interface Message {
  id: string;
  role: InterviewRole;
  content: string;
  stage?: string | null;
  answer_quality?: string | null;
  detected_issues?: string[] | null;
  brief_feedback?: string | null;
  created_at: string;
}

export interface CreateInterviewResponse {
  interview_id: string;
  first_question: string;
  current_stage: string;
}

export interface InterviewDetail {
  id: string;
  type: string;
  interviewer_style: string;
  target_school?: string | null;
  target_major?: string | null;
  current_stage: string;
  status: string;
  total_score?: number | null;
  created_at: string;
  messages: Message[];
}

export interface InterviewListItem {
  id: string;
  type: string;
  interviewer_style: string;
  target_school?: string | null;
  target_major?: string | null;
  status: string;
  total_score?: number | null;
  created_at: string;
}

export interface SendAnswerResponse {
  reply: string;
  stage: string;
  action: 'follow_up' | 'next_question' | 'end_interview';
}

export interface FinishInterviewResponse {
  report_id: string;
  total_score: number;
}
