import { httpClient } from "./http";

export interface QuizQuestion {
  id: number;
  title: string;
  options: string[];
  active_date: string;
  points_reward: number;
}

export interface QuizAnswerResult {
  question_id: number;
  is_correct: boolean;
  points_reward: number;
  message: string;
  created_at: string;
}

export async function fetchTodayQuestion(): Promise<QuizQuestion> {
  const { data } = await httpClient.get<{ data: QuizQuestion }>("/quiz/today");
  return data.data;
}

export async function submitQuizAnswer(questionId: number, selectedOption: string): Promise<QuizAnswerResult> {
  const { data } = await httpClient.post<{ data: QuizAnswerResult }>("/quiz/answer", {
    question_id: questionId,
    selected_option: selectedOption
  });
  return data.data;
}
