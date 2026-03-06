import { httpClient } from "./http";

export interface ActivityItem {
  id: number;
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
  quota: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PaginationMeta { page: number; page_size: number; total: number }

export async function fetchActivities(params: { status?: string; page?: number; pageSize?: number } = {}) {
  const { status, page = 1, pageSize = 10 } = params;
  const { data } = await httpClient.get<{ data: ActivityItem[]; meta?: PaginationMeta }>("/activities", {
    params: { status, page, page_size: pageSize }
  });
  return data;
}

export async function enrollActivity(id: number): Promise<void> {
  await httpClient.post(`/activities/${id}/enroll`, {});
}

// 占位：若后端提供“我的报名”列表接口，可在此实现
export async function fetchMyEnrollments(params: { page?: number; pageSize?: number } = {}) {
  const { page = 1, pageSize = 10 } = params;
  const { data } = await httpClient.get<{ data: ActivityItem[]; meta?: PaginationMeta }>("/activities/enrollments/me", {
    params: { page, page_size: pageSize }
  });
  return data;
}
