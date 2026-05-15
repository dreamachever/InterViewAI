import { apiClient } from './client';
import type { LoginRequest, RegisterRequest, RegisterResponse, TokenResponse } from '../types/auth';

export async function register(payload: RegisterRequest) {
  const { data } = await apiClient.post<RegisterResponse>('/auth/register', payload);
  return data;
}

export async function login(payload: LoginRequest) {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', payload);
  return data;
}
