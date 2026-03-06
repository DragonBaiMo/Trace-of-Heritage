import { httpClient } from "./http";

export interface ResourceTrail {
  id?: number;
  place_name: string;
  region_code?: string | null;
  longitude: number;
  latitude: number;
  occurred_at?: string | null;
  order_no: number;
}

export interface ResourceItem {
  id: number;
  title: string;
  resource_type: string;
  synopsis: string | null;
  tags: string[];
  status: string;
  file_path: string | null;
  external_url: string | null;
  created_at: string;
  updated_at: string;
  submitter_id: number;
  reviewer_id: number | null;
  review_note: string | null;
  trails: ResourceTrail[];
}

export interface ResourceCreatePayload {
  title: string;
  resource_type: string;
  synopsis?: string;
  tags?: string[];
  era?: string;
  genre?: string;
  region_code?: string;
  author?: string;
  copyright_status?: string;
  file_path?: string;
  external_url?: string;
  submit_for_review?: boolean;
  trails?: ResourceTrail[];
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface ResourceQuery {
  status?: string;
  keyword?: string;
  page?: number;
  pageSize?: number;
}

export interface ResourceListResult {
  items: ResourceItem[];
  meta: PaginationMeta;
}

export interface ResourceSummary {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  latest: ResourceItem[];
}

export async function fetchResources(query: ResourceQuery = {}): Promise<ResourceListResult> {
  const { status, keyword, page = 1, pageSize = 10 } = query;
  const { data } = await httpClient.get<{ data: ResourceItem[]; meta: PaginationMeta }>("/resources", {
    params: {
      status,
      keyword,
      page,
      page_size: pageSize
    }
  });
  return {
    items: data.data,
    meta:
      data.meta ?? {
        page,
        page_size: pageSize,
        total: data.data.length
      }
  };
}

export async function fetchResourceSummary(): Promise<ResourceSummary> {
  const { data } = await httpClient.get<{ data: ResourceSummary }>("/resources/summary");
  return data.data;
}

export async function createResource(payload: ResourceCreatePayload): Promise<ResourceItem> {
  const { data } = await httpClient.post<{ data: ResourceItem }>("/resources", payload);
  return data.data;
}

export async function fetchResourceDetail(id: number): Promise<ResourceItem> {
  const { data } = await httpClient.get<{ data: ResourceItem }>(`/resources/${id}`);
  return data.data;
}

export async function updateResource(id: number, payload: Partial<ResourceCreatePayload>): Promise<ResourceItem> {
  const { data } = await httpClient.patch<{ data: ResourceItem }>(`/resources/${id}`, payload);
  return data.data;
}

export async function fetchTrails(resourceId: number): Promise<ResourceTrail[]> {
  const { data } = await httpClient.get<{ data: ResourceTrail[] }>(`/resources/${resourceId}/trails`);
  return data.data;
}
