import { apiClient } from "./client";

export interface User {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
  phone?: string;
  organization_id?: string;
}

export const authApi = {
  getMe: async (): Promise<User> => {
    const { data } = await apiClient.get("/auth/me");
    return data;
  },
  login: async (credentials: any) => {
    const { data } = await apiClient.post("/auth/login", credentials);
    return data;
  },
};
