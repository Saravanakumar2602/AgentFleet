import axios, { AxiosError, type AxiosResponse } from "axios";

export const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: { "Content-Type": "application/json" },
});

// ── Response interceptor: unwrap data, surface errors ─────────────────────
api.interceptors.response.use(
  (res: AxiosResponse) => res,
  (err: AxiosError<{ message?: string; status?: string }>) => {
    const message =
      err.response?.data?.message ??
      err.message ??
      "An unexpected error occurred.";
    // Attach a clean message so hooks can surface it directly
    return Promise.reject(new Error(message));
  }
);
