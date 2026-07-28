import { useQuery, useQueries, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { fleetService } from "../services/fleet";
import type { MaintenanceResult } from "../types/api";

// Keep static fallback definition in case backend is offline/error
export const FLEET_VEHICLE_IDS = [
  { id: "v1", number: "TN38AB1234", type: "Dry Van",    capacity: "3,000 kg", driver: "Ravi K." },
  { id: "v2", number: "TN38CD5678", type: "Flatbed",    capacity: "5,000 kg", driver: "Suresh P." },
  { id: "v3", number: "TN38EF9012", type: "Reefer",     capacity: "1,500 kg", driver: "Arun M." },
  { id: "v4", number: "KA-RT-8011", type: "Heavy Duty", capacity: "8,000 kg", driver: "—" },
  { id: "v5", number: "MH12AB3456", type: "Dry Van",    capacity: "2,500 kg", driver: "Kiran S." },
  { id: "v6", number: "TN45GH7890", type: "Flatbed",    capacity: "4,000 kg", driver: "Priya R." },
];

export interface FleetVehicleData {
  id: string;
  number: string;
  type: string;
  capacity: string;
  driver: string;
  status: string;
  health_score: number;
  health: MaintenanceResult | null;
  isLoading: boolean;
  isError: boolean;
}

export const useFleet = () => {
  const queryClient = useQueryClient();

  const vehiclesQuery = useQuery({
    queryKey: ["fleet", "vehicles"],
    queryFn: fleetService.getVehicles,
    staleTime: 60_000,
  });

  const vehiclesList = vehiclesQuery.data ?? [];

  const results = useQueries({
    queries: vehiclesList.map((v: any) => ({
      queryKey: ["fleet", "vehicle", v.id],
      queryFn: () => fleetService.getVehicleHealth(v.id),
      retry: 1,
      staleTime: 60_000,
    })),
  });

  const vehicles: FleetVehicleData[] = vehiclesList.map((v: any, i: number) => ({
    id: v.id,
    number: v.number,
    type: v.type,
    capacity: v.capacity,
    driver: v.driver,
    status: v.status,
    health_score: v.health_score,
    health: results[i]?.data ?? null,
    isLoading: results[i]?.isLoading || false,
    isError: results[i]?.isError || false,
  }));

  const isLoading = vehiclesQuery.isLoading;
  const isError = vehiclesQuery.isError || (vehiclesList.length > 0 && results.every((r) => r.isError));

  const refetch = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["fleet"] });
  }, [queryClient]);

  return { vehicles, isLoading, isError, refetch };
};

