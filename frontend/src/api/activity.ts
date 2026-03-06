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

export interface ActivityCreatePayload {
  title: string;
  description: string;
  location: string;
  start_time: string;
  end_time: string;
  quota: number;
  submit_for_review?: boolean;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface ActivityListResult {
  items: ActivityItem[];
  meta: PaginationMeta;
}

export async function fetchActivities(status?: string): Promise<ActivityListResult> {
  const { data } = await httpClient.get<{ data: ActivityItem[]; meta: PaginationMeta }>("/activities", {
    params: {
      status
    }
  });
  return {
    items: data.data,
    meta: data.meta
  };
}

export async function createActivity(payload: ActivityCreatePayload): Promise<ActivityItem> {
  const { data } = await httpClient.post<{ data: ActivityItem }>("/activities", payload);
  return data.data;
}

export async function enrollActivity(activityId: number): Promise<void> {
  await httpClient.post(`/activities/${activityId}/enroll`);
}

export async function checkinActivity(activityId: number): Promise<void> {
  await httpClient.post(`/activities/${activityId}/checkin`);
}
