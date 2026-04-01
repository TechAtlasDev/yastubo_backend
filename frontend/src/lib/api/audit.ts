import { apiClient } from "./client";

export interface AuditLog {
  id: string;
  user_id: string;
  user_name?: string;
  action: string;
  entity: string;
  entity_id: string;
  details: any;
  created_at: string;
  ip_address?: string;
}

export interface PaginatedAuditResponse {
  items: AuditLog[];
  total: number;
  page: number;
  page_size: number;
}

export const auditApi = {
  getLogs: async (params: {
    entity?: string;
    entity_id?: string;
    user_id?: string;
    action?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedAuditResponse> => {
    const { data } = await apiClient.get("/audit/", { params });
    return data;
  },
};
