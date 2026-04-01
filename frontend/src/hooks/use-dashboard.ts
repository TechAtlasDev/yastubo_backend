import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ["dashboard-metrics"],
    queryFn: async () => {
      const { data } = await apiClient.get("/dashboard/metrics");
      return data;
    },
  });
};

export const useActivityFeed = () => {
  return useQuery({
    queryKey: ["activity-feed"],
    queryFn: async () => {
      const { data } = await apiClient.get("/audit/logs?limit=5");
      return data;
    },
  });
};
