export type LLMProvider = 'mock' | 'openai' | 'deepseek' | 'tongyi' | 'doubao' | 'custom_openai_compatible';

export interface LLMConfig {
  id: string;
  display_name: string;
  provider: LLMProvider;
  base_url?: string | null;
  model?: string | null;
  is_active: boolean;
  is_default: boolean;
  has_api_key: boolean;
  last_test_status?: string | null;
  last_test_message?: string | null;
  last_tested_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface LLMConfigPayload {
  display_name: string;
  provider: LLMProvider;
  base_url?: string | null;
  model?: string | null;
  api_key?: string | null;
  is_active?: boolean;
  is_default?: boolean;
}

export interface LLMConfigTestResult {
  status: string;
  message: string;
}
