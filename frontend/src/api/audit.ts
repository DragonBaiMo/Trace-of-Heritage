import { httpClient } from "./http";

export interface AuditLogItem {
  id: number;
  actor_id: number;
  action: string;
  target_type: string;
  target_id: string;
  note: string | null;
  ip: string | null;
  created_at: string;
}

export async function fetchAuditLogs(limit = 20): Promise<AuditLogItem[]> {
  const { data } = await httpClient.get<{ data: AuditLogItem[] }>("/audits", {
    params: { limit }
  });
  return data.data;
}
