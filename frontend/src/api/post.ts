import { httpClient } from "./http";

export interface PostItem {
  id: number;
  title: string;
  content_md: string;
  topic: string | null;
  status: string;
  like_count: number;
  favorite_count: number;
  created_at: string;
  updated_at: string;
}

export interface CommentItem {
  id: number;
  post_id: number;
  author_id: number;
  content: string;
  status: string;
  created_at: string;
}

export interface PostQuery {
  status?: string;
  topic?: string;
  page?: number;
  pageSize?: number;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
}

export interface PostListResult {
  items: PostItem[];
  meta: PaginationMeta;
}

export interface PostCreatePayload {
  title: string;
  content_md: string;
  topic?: string;
  submit_for_review?: boolean;
}

export interface CommentPayload {
  content: string;
}

export interface ReactionPayload {
  reaction_type: "like" | "favorite";
  target_type: "post" | "resource";
  target_id: number;
}

export async function fetchPosts(query: PostQuery = {}): Promise<PostListResult> {
  const { status, topic, page = 1, pageSize = 8 } = query;
  const { data } = await httpClient.get<{ data: PostItem[]; meta: PaginationMeta }>("/posts/", {
    params: {
      status,
      topic,
      page,
      page_size: pageSize
    }
  });
  return {
    items: data.data,
    meta: data.meta
  };
}

export async function createPost(payload: PostCreatePayload): Promise<PostItem> {
  const { data } = await httpClient.post<{ data: PostItem }>("/posts/", payload);
  return data.data;
}

export async function createComment(postId: number, payload: CommentPayload): Promise<CommentItem> {
  const { data } = await httpClient.post<{ data: CommentItem }>(`/posts/${postId}/comments`, payload);
  return data.data;
}

export async function fetchComments(postId: number): Promise<CommentItem[]> {
  const { data } = await httpClient.get<{ data: CommentItem[] }>(`/posts/${postId}/comments`);
  return data.data;
}

export async function sendReaction(payload: ReactionPayload): Promise<void> {
  await httpClient.post("/posts/reactions", payload);
}
