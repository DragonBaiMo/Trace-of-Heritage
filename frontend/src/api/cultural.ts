import { httpClient } from "./http";

export interface VideoRecommendation {
  id: number;
  title: string;
  description?: string | null;
  platform: string;
  url: string;
  thumbnail_url?: string | null;
  opera_genre?: string | null;
  duration_display?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface WeeklyDigestItem {
  title: string;
  url: string;
  type: "article" | "video";
  desc?: string | null;
}

export interface WeeklyDigest {
  id: number;
  year: number;
  week_number: number;
  title: string;
  summary?: string | null;
  items: WeeklyDigestItem[];
  published_at?: string | null;
  is_published: boolean;
  created_at: string;
}

export interface PaginationMeta { page: number; page_size: number; total: number }

export async function fetchVideoRecommendations(params: { genre?: string; page?: number; pageSize?: number } = {}) {
  const { genre, page = 1, pageSize = 20 } = params;
  const { data } = await httpClient.get<{ data: VideoRecommendation[]; meta: PaginationMeta }>("/cultural/videos", {
    params: { genre, page, page_size: pageSize }
  });
  return data;
}

export async function fetchWeeklyDigests(params: { page?: number; pageSize?: number } = {}) {
  const { page = 1, pageSize = 10 } = params;
  const { data } = await httpClient.get<{ data: WeeklyDigest[]; meta: PaginationMeta }>("/cultural/weekly", {
    params: { page, page_size: pageSize }
  });
  return data;
}

export async function fetchLatestDigest(): Promise<WeeklyDigest | null> {
  const { data } = await httpClient.get<{ data: WeeklyDigest | null }>("/cultural/weekly/latest");
  return data.data;
}
