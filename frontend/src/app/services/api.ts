import axios, { AxiosError, type AxiosResponse } from "axios";

export const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

// ── Response interceptor: unwrap data, surface errors ─────────────────────
api.interceptors.response.use(
  (res: AxiosResponse) => res,
  (err: AxiosError<{ message?: string; reason?: string; failed_agent?: string; status?: string }>) => {
    const data = err.response?.data;
    let message = err.message ?? "An unexpected error occurred.";

    if (data) {
      if (data.failed_agent && data.reason) {
        message = `${data.failed_agent} Agent: ${data.reason}`;
      } else if (data.reason) {
        message = data.reason;
      } else if (data.message) {
        message = data.message;
      }
    }

    // Attach a clean message so hooks can surface it directly
    return Promise.reject(new Error(message));
  }
);
