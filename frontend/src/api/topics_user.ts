import { httpClient } from "./http";
import type { PaginationMeta, PostItem } from "./post";

export async function fetchHotPosts(params: { page?: number; pageSize?: number } = {}) {
  const { page = 1, pageSize = 10 } = params;
  // 后端已有 /api/posts 列表；此处采用 status=approved 作为基础过滤
  const { data } = await httpClient.get<{ data: PostItem[]; meta?: PaginationMeta }>("/posts/", {
    params: { status: "approved", page, page_size: pageSize }
  });
  return data;
}
