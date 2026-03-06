import { httpClient } from "./http";

export interface TrendPoint {
  day: string;
  count: number;
}

export interface CategoryValue {
  name: string;
  value: number;
}

export interface ActivityStat {
  title: string;
  enrolled: number;
  checked_in: number;
}

export interface DashboardStats {
  resource_trend: TrendPoint[];
  topic_hot: CategoryValue[];
  region_distribution: CategoryValue[];
  activity_participants: ActivityStat[];
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const { data } = await httpClient.get<{ data: DashboardStats }>("/stats/dashboard");
  return data.data;
}
