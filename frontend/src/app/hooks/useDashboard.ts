import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "../services/dashboard";

export const useDashboard = () => {
  const system = useQuery({
    queryKey: ["health", "system"],
    queryFn: dashboardService.getSystemHealth,
    refetchInterval: 30_000,
    retry: 2,
  });

  const db = useQuery({
    queryKey: ["health", "database"],
    queryFn: dashboardService.getDatabaseHealth,
    refetchInterval: 30_000,
    retry: 2,
  });

  const stats = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: dashboardService.getStats,
    refetchInterval: 15_000,
    retry: 2,
  });

  const isOnline = system.data?.status === "success" || system.data?.message?.includes("online");
  const isDbConnected = db.data?.status === "connected" || db.data?.status === "success";

  return {
    isOnline,
    isDbConnected,
    stats: stats.data ?? null,
    isLoading: system.isLoading || db.isLoading || stats.isLoading,
    isError: system.isError || db.isError || stats.isError,
    error: system.error ?? db.error ?? stats.error,
    refetch: () => {
      system.refetch();
      db.refetch();
      stats.refetch();
    },
  };
};

