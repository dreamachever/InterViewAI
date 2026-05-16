import { apiClient } from './client';
import type { LLMConfig, LLMConfigPayload, LLMConfigTestResult } from '../types/llmConfig';

export async function listLLMConfigs() {
  const { data } = await apiClient.get<LLMConfig[]>('/llm-configs');
  return data;
}

export async function createLLMConfig(payload: LLMConfigPayload) {
  const { data } = await apiClient.post<LLMConfig>('/llm-configs', payload);
  return data;
}

export async function updateLLMConfig(configId: string, payload: Partial<LLMConfigPayload>) {
  const { data } = await apiClient.patch<LLMConfig>(`/llm-configs/${configId}`, payload);
  return data;
}

export async function deleteLLMConfig(configId: string) {
  await apiClient.delete(`/llm-configs/${configId}`);
}

export async function testLLMConfig(configId: string) {
  const { data } = await apiClient.post<LLMConfigTestResult>(`/llm-configs/${configId}/test`);
  return data;
}

export async function setDefaultLLMConfig(configId: string) {
  const { data } = await apiClient.post<LLMConfig>(`/llm-configs/${configId}/set-default`);
  return data;
}
