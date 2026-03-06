import { httpClient } from "./http";
import type { ResourceItem } from "./resource";

export async function fetchRecommendations(limit = 6) {
  const { data } = await httpClient.get<{ data: ResourceItem[] }>("/recommendations", { params: { limit } });
  return data.data;
}
