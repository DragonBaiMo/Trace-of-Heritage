import axios from "axios";

// 默认对齐后端本地监听地址，避免 localhost/127.0.0.1 混用引发额外排障成本
const apiBase = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api";

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

    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return Promise.reject(detail);
    }

    if (typeof error.response?.status === "number") {
      return Promise.reject(`请求失败（HTTP ${error.response.status}）`);
    }

    return Promise.reject(
      error.message ?? "请求失败"
    );
  }
);
