import { apiClient } from "./client";

export interface Policy {
  id: string;
  policy_number: string;
  status: string;
  client_name: string;
  plan_name: string;
  premium_amount: number;
  created_at: string;
  start_date: string;
  end_date: string;
  next_payment_date?: string;
}

export interface EmissionStats {
  active_count: number;
  pending_payment_count: number;
  cancelled_count: number;
  total_premium: number;
  retention_rate: number;
  claims_count: number;
}

export const emissionApi = {
  listPolicies: async (params?: { status?: string; search?: string }) => {
    const response = await apiClient.get<Policy[]>("/emission/policies", { params });
    return response.data;
  },

  getStats: async () => {
    const response = await apiClient.get<EmissionStats>("/emission/stats");
    return response.data;
  },

  registerClient: async (data: any) => {
    const response = await apiClient.post("/emission/clients", data);
    return response.data;
  },

  issuePolicy: async (data: { client_id: string; plan_version_id: string }) => {
    const response = await apiClient.post("/emission/policies", data);
    return response.data;
  },
};
