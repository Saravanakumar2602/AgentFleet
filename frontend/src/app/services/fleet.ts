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
    const res = await api.post<MaintenanceResult>("/maintenance", {
      vehicle_id: vehicleId,
    });
    return res.data;
  },
};

