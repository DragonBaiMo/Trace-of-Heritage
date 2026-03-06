import { httpClient } from "./http";

export interface UserItem {
  id: number;
  username: string;
  nickname?: string | null;
  avatar?: string | null;
  bio?: string | null;
  role: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface UserUpdatePayload {
  nickname?: string | null;
  avatar?: string | null;
  bio?: string | null;
  role?: string;
  status?: string;
  password?: string; // 重置密码
}

export async function fetchUsers(): Promise<UserItem[]> {
  const { data } = await httpClient.get<{ data: UserItem[] }>("/users");
  return data.data;
}

export async function updateUser(id: number, payload: UserUpdatePayload): Promise<UserItem> {
  const { data } = await httpClient.patch<{ data: UserItem }>(`/users/${id}`, payload);
  return data.data;
}
