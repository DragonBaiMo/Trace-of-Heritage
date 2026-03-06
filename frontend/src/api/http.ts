import axios from "axios";

const apiBase = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

export const httpClient = axios.create({
  baseURL: apiBase,
  timeout: 10000
});

httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

httpClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(
      error.response?.data?.detail ?? error.message ?? "请求失败"
    );
  }
);
