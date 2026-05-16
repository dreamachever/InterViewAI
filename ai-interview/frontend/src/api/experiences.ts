import { apiClient } from './client';
import type {
  ExperienceDetail,
  ExperienceImportPayload,
  ExperienceImportWebPayload,
  ExperienceListItem,
  ExperienceSearchPayload,
  ExperienceSearchResponse,
  ExperienceUpdatePayload,
} from '../types/experience';

export interface ExperienceFilters {
  target_school?: string;
  target_major?: string;
  interview_type?: string;
  source_type?: string;
}

export async function listExperiences(filters: ExperienceFilters = {}) {
  const { data } = await apiClient.get<ExperienceListItem[]>('/experiences', { params: filters });
  return data;
}

export async function getExperience(experienceId: string) {
  const { data } = await apiClient.get<ExperienceDetail>(`/experiences/${experienceId}`);
  return data;
}

export async function importExperienceText(payload: ExperienceImportPayload) {
  const { data } = await apiClient.post<{ experience_id: string; extract_status: string }>('/experiences/import-text', payload);
  return data;
}

export async function searchExperienceWeb(payload: ExperienceSearchPayload) {
  const { data } = await apiClient.post<ExperienceSearchResponse>('/experiences/search-web', payload);
  return data;
}

export async function importExperienceWeb(payload: ExperienceImportWebPayload) {
  const { data } = await apiClient.post<{ experience_id: string; extract_status: string }>('/experiences/import-web', payload);
  return data;
}

export async function updateExperience(experienceId: string, payload: ExperienceUpdatePayload) {
  const { data } = await apiClient.patch<ExperienceDetail>(`/experiences/${experienceId}`, payload);
  return data;
}

export async function deleteExperience(experienceId: string) {
  await apiClient.delete(`/experiences/${experienceId}`);
}

export async function extractExperience(experienceId: string, llm_config_id?: string | null) {
  const { data } = await apiClient.post<ExperienceDetail>(`/experiences/${experienceId}/extract`, { llm_config_id: llm_config_id || null });
  return data;
}
