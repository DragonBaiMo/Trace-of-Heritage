import { httpClient } from "./http";

export interface PractitionerApplicationItem {
  id: number;
  applicant_id: number;
  realname: string;
  title: string;
  bio?: string | null;
  attachment?: string | null;
  status: "pending" | "approved" | "rejected";
  reviewer_id?: number | null;
  review_note?: string | null;
  created_at: string;
  updated_at: string;
}

export interface PractitionerReviewPayload {
  decision: "approve" | "reject";
  review_note?: string;
}

export async function fetchApplications(status?: string): Promise<PractitionerApplicationItem[]> {
  const { data } = await httpClient.get<{ data: PractitionerApplicationItem[] }>("/practitioners/applications", {
    params: { status }
  });
  return data.data;
}

export async function reviewApplication(id: number, payload: PractitionerReviewPayload): Promise<PractitionerApplicationItem> {
  const { data } = await httpClient.post<{ data: PractitionerApplicationItem }>(`/practitioners/applications/${id}/review`, payload);
  return data.data;
}
