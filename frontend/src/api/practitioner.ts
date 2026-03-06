import { httpClient } from "./http";

export interface ApplyPayload {
  realname: string;
  title: string;
  bio?: string;
  attachment?: string;
}

export interface ApplicationRead {
  id: number;
  realname: string;
  title: string;
  bio?: string | null;
  attachment?: string | null;
  status: string;
  applicant_id: number;
  reviewer_id?: number | null;
  review_note?: string | null;
  created_at: string;
  updated_at: string;
}

export async function applyPractitioner(payload: ApplyPayload): Promise<ApplicationRead> {
  const { data } = await httpClient.post<{ data: ApplicationRead }>("/practitioners/apply", payload);
  return data.data;
}

export async function listApplications(): Promise<ApplicationRead[]> {
  const { data } = await httpClient.get<{ data: ApplicationRead[] }>("/practitioners/applications");
  return data.data;
}

export async function reviewApplication(id: number, decision: "approve" | "reject", review_note?: string): Promise<ApplicationRead> {
  const { data } = await httpClient.post<{ data: ApplicationRead }>(`/practitioners/applications/${id}/review`, { decision, review_note });
  return data.data;
}
