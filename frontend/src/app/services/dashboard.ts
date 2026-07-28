import { api } from "./api";
import type { HealthResponse } from "../types/api";

export const dashboardService = {
  getSystemHealth: async (): Promise<HealthResponse> => {
    const res = await api.get<HealthResponse>("/health");
    return res.data;
  },

  getDatabaseHealth: async (): Promise<{ status: string; database: string }> => {
    const res = await api.get<{ status: string; database: string }>("/health/database");
    return res.data;
  },

  getStats: async (): Promise<any> => {
    const res = await api.get<any>("/dashboard/stats");
    return res.data.data ?? res.data;
  },
};

