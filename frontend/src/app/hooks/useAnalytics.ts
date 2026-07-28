import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../services/analytics";
import { FLEET_VEHICLE_IDS } from "./useFleet";

export const useAnalytics = (vehicleId?: string) => {
  const id = vehicleId ?? FLEET_VEHICLE_IDS[0].id;

  const query = useQuery({
    queryKey: ["analytics", id],
    queryFn: () => analyticsService.getVehicleReport(id),
    retry: 1,
    staleTime: 120_000,
  });

  return {
    data: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
};
