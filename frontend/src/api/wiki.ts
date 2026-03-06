import { httpClient } from "./http";

export interface WikiEntry {
  id: number;
  title: string;
  content: string;
  category?: string | null;
  status: string;
  author_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface PaginationMeta { page: number; page_size: number; total: number }

export async function fetchWikiEntries(params: { keyword?: string; category?: string; page?: number; pageSize?: number } = {}) {
  const { keyword, category, page = 1, pageSize = 10 } = params;
  const { data } = await httpClient.get<{ data: WikiEntry[]; meta: PaginationMeta }>("/wiki/entries", {
    params: { keyword, category, page, page_size: pageSize }
  });
  return data;
}

export async function fetchWikiEntry(id: number) {
  const { data } = await httpClient.get<{ data: WikiEntry }>(`/wiki/entries/${id}`);
  return data.data;
}
