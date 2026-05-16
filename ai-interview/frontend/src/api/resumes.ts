import { apiClient } from './client';
import type { Resume, ResumeDetail, ResumeDiagnostic } from '../types/resume';

export async function uploadResume(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<ResumeDetail>('/resumes/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function listResumes() {
  const { data } = await apiClient.get<Resume[]>('/resumes');
  return data;
}

export async function getResume(resumeId: string) {
  const { data } = await apiClient.get<ResumeDetail>(`/resumes/${resumeId}`);
  return data;
}

export async function updateResume(resumeId: string, payload: { title?: string; parsed_text?: string; is_default?: boolean }) {
  const { data } = await apiClient.patch<ResumeDetail>(`/resumes/${resumeId}`, payload);
  return data;
}

export async function reparseResume(resumeId: string) {
  const { data } = await apiClient.post<ResumeDetail>(`/resumes/${resumeId}/reparse`);
  return data;
}

export async function deleteResume(resumeId: string) {
  await apiClient.delete(`/resumes/${resumeId}`);
}

export async function diagnoseResume(resumeId: string, llmConfigId?: string | null) {
  const { data } = await apiClient.post<ResumeDiagnostic>(`/resumes/${resumeId}/diagnose`, {
    llm_config_id: llmConfigId || null,
  });
  return data;
}

export async function listResumeDiagnostics(resumeId: string) {
  const { data } = await apiClient.get<ResumeDiagnostic[]>(`/resumes/${resumeId}/diagnostics`);
  return data;
}
