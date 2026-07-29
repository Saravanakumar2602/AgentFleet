import { api } from "./api";
import type { AnalyticsResult } from "../types/api";

export const analyticsService = {
  /** POST /analytics/report — generate fleet analytics for a vehicle */
  getVehicleReport: async (vehicleId: string): Promise<AnalyticsResult> => {
    const res = await api.post<any>("/analytics/report", {
      vehicle_id: vehicleId,
    });
    const envelope = res.data;
    return {
      status: envelope.status,
      message: envelope.message,
      agent: envelope.data?.agent ?? "Fleet Analytics Agent",
      vehicle: envelope.data?.vehicle,
      total_trips: envelope.data?.total_trips ?? 0,
      average_distance: envelope.data?.average_distance ?? 0.0,
      fuel_efficiency: envelope.data?.fuel_efficiency ?? 0.0,
      maintenance_count: envelope.data?.maintenance_count ?? 0,
      utilization: envelope.data?.utilization ?? 0,
      recommendation: envelope.data?.recommendation ?? "Vehicle operating normally.",
    };
  },
  /** GET /analytics/historical — retrieve historical analytics chart metrics */
  getHistoricalAnalytics: async (): Promise<{ points: number[]; months: string[] }> => {
    const res = await api.get<{ points: number[]; months: string[] }>("/analytics/historical");
    return (res.data as any).data ?? res.data;
  },
};
