import { httpClient } from "./http";

interface LoginPayload {
  username: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserProfile {
  id: number;
  username: string;
  nickname: string | null;
  avatar: string | null;
  role: string;
  status: string;
  email?: string | null;
  updated_at?: string | null;
}

export async function loginRequest(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await httpClient.post<{ data: TokenResponse }>("/auth/login", payload);
  return data.data;
}

export async function fetchProfile(): Promise<UserProfile> {
  const { data } = await httpClient.get<{ data: UserProfile }>("/users/me");
  return data.data;
}

export interface RegisterPayload {
  username: string;
  password: string;
  nickname?: string;
}

export async function register(payload: RegisterPayload): Promise<UserProfile> {
  const { data } = await httpClient.post<{ data: UserProfile }>("/auth/register", payload);
  return data.data;
}
