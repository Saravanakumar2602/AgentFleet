import { api } from "./api";
import type { MaintenanceResult } from "../types/api";

export const fleetService = {
  /** GET /vehicles — retrieve all fleet vehicles */
  getVehicles: async (): Promise<any[]> => {
    const res = await api.get<any[]>("/vehicles");
    return (res.data as any).data ?? res.data;
  },

  /** POST /maintenance — evaluate a single vehicle's health */
  getVehicleHealth: async (vehicleId: string): Promise<MaintenanceResult> => {
    const res = await api.post<any>("/maintenance", {
      vehicle_id: vehicleId,
    });
    const envelope = res.data;
    return {
      status: envelope.status,
      message: envelope.message,
      agent: envelope.data?.agent ?? "Maintenance Agent",
      vehicle_id: envelope.data?.vehicle_id,
      health_score: envelope.data?.health_score ?? 100,
      vehicle_status: envelope.data?.vehicle_status ?? "Healthy",
      next_service_after_km: envelope.data?.next_service_after_km,
    };
  },
};

