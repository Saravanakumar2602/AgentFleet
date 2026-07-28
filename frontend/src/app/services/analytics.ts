import { api } from "./api";
import type { AnalyticsResult } from "../types/api";

export const analyticsService = {
  /** POST /analytics/report — generate fleet analytics for a vehicle */
  getVehicleReport: async (vehicleId: string): Promise<AnalyticsResult> => {
    const res = await api.post<AnalyticsResult>("/analytics/report", {
      vehicle_id: vehicleId,
    });
    return res.data;
  },
};
