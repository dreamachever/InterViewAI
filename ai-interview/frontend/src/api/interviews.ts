import { apiClient } from './client';
import type {
  CreateInterviewResponse,
  FinishInterviewResponse,
  InterviewConfig,
  InterviewDetail,
  SendAnswerResponse,
} from '../types/interview';
import type { Report } from '../types/report';

export async function createInterview(payload: InterviewConfig) {
  const { data } = await apiClient.post<CreateInterviewResponse>('/interviews', payload);
  return data;
}

export async function getInterview(interviewId: string) {
  const { data } = await apiClient.get<InterviewDetail>(`/interviews/${interviewId}`);
  return data;
}

export async function sendAnswer(interviewId: string, answer: string) {
  const { data } = await apiClient.post<SendAnswerResponse>(`/interviews/${interviewId}/messages`, { answer });
  return data;
}

export async function finishInterview(interviewId: string) {
  const { data } = await apiClient.post<FinishInterviewResponse>(`/interviews/${interviewId}/finish`);
  return data;
}

export async function getReport(interviewId: string) {
  const { data } = await apiClient.get<Report>(`/interviews/${interviewId}/report`);
  return data;
}
