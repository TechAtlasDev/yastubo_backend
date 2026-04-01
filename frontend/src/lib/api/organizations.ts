import { apiClient } from "./client";

export interface Company {
  id: string;
  name: string;
  tax_id: string;
  email: string;
  phone?: string;
  address?: string;
  is_active: boolean;
  branding_logo_url?: string;
  created_at: string;
}

export interface BusinessUnit {
  id: string;
  company_id: string;
  name: string;
  code: string;
  is_active: boolean;
  created_at: string;
}

export const organizationsApi = {
  getCompanies: async (): Promise<Company[]> => {
    const { data } = await apiClient.get("/organizations/companies");
    return data;
  },
  getCompany: async (id: string): Promise<Company> => {
    const { data } = await apiClient.get(`/organizations/companies/${id}`);
    return data;
  },
  createCompany: async (company: Partial<Company>): Promise<Company> => {
    const { data } = await apiClient.post("/organizations/companies", company);
    return data;
  },
  getBusinessUnits: async (companyId: string): Promise<BusinessUnit[]> => {
    const { data } = await apiClient.get(
      `/organizations/companies/${companyId}/business-units`
    );
    return data;
  },
  createBusinessUnit: async (
    companyId: string,
    unit: Partial<BusinessUnit>
  ): Promise<BusinessUnit> => {
    const { data } = await apiClient.post(
      `/organizations/companies/${companyId}/business-units`,
      unit
    );
    return data;
  },
};
