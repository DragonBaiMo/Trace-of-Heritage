import { httpClient } from "./http";

export interface AISynopsisResult {
  synopsis: string;
  tags: string[];
}

export async function generateSynopsis(content: string, expectLength = 120): Promise<AISynopsisResult> {
  const { data } = await httpClient.post<{ data: AISynopsisResult }>("/ai/synopsis", {
    content,
    expect_length: expectLength
  });
  return data.data;
}
