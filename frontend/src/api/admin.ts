import { httpClient } from "./http";

export interface ReviewPayload {
  decision: "approve" | "reject";
  review_note?: string;
}

// Resources
export async function listPendingResources() {
  const { data } = await httpClient.get("/resources", { params: { status: "pending", page: 1, page_size: 50 } });
  return data.data;
}

export async function reviewResource(id: number, payload: ReviewPayload) {
  const { data } = await httpClient.post(`/resources/${id}/review`, null, {
    params: { decision: payload.decision, review_note: payload.review_note }
  });
  return data.data;
}

// Activities
export async function listPendingActivities() {
  const { data } = await httpClient.get("/activities", { params: { status: "pending", page: 1, page_size: 50 } });
  return data.data;
}

export async function reviewActivity(id: number, payload: ReviewPayload) {
  const { data } = await httpClient.post(`/activities/${id}/review`, payload);
  return data.data;
}

// Posts
export async function listPendingPosts() {
  const { data } = await httpClient.get("/posts", { params: { status: "pending", page: 1, page_size: 50 } });
  return data.data;
}

export async function reviewPost(id: number, payload: ReviewPayload) {
  // posts 没有专门 review 端点，使用 PATCH 更新 status 与 review_note
  const body: any = { status: payload.decision === "approve" ? "approved" : "rejected" };
  if (payload.review_note) body.review_note = payload.review_note;
  const { data } = await httpClient.patch(`/posts/${id}`, body);
  return data.data;
}
