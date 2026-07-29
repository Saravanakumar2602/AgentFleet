import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../services/analytics";

export const useAnalytics = (vehicleId?: string) => {
  const query = useQuery({
    queryKey: ["analytics", vehicleId],
    queryFn: () => analyticsService.getVehicleReport(vehicleId!),
    enabled: !!vehicleId,
    retry: 1,
    staleTime: 120_000,
  });

  return {
    data: query.data ?? null,
    isLoading: query.isLoading || !vehicleId,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
};

export const useHistoricalAnalytics = () => {
  const query = useQuery({
    queryKey: ["analytics", "historical"],
    queryFn: () => analyticsService.getHistoricalAnalytics(),
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
