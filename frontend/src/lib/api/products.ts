import { apiClient } from "./client";
import { 
  Product, 
  PriceCalculationRequest, 
  PriceCalculationResponse,
  CurrencyCode 
} from "./types/catalog";

// Types for creation and updates
export interface CoverageCreate {
  name: string;
  description?: string;
  limit_amount: number;
  is_optional: boolean;
  waiting_period_days: number;
}

export interface AgeSurchargeCreate {
  min_age: number;
  max_age: number;
  surcharge_percentage: number;
}

export interface PlanCountryCreate {
  country_code: string;
  is_available: boolean;
  override_price?: number;
}

export interface PlanVersionCreate {
  cost_price: number;
  public_price: number;
  currency: CurrencyCode;
  max_entry_age: number;
  max_renewal_age: number;
  wtime_suicide: number;
  wtime_accident: number;
  wtime_preexisting: number;
  coverages?: CoverageCreate[];
  age_surcharges?: AgeSurchargeCreate[];
  countries?: PlanCountryCreate[];
}

export interface PlanCreate {
  name: string;
  description?: string;
  company_id?: string;
  versions?: PlanVersionCreate[];
}

export interface ProductCreate {
  name: string;
  description?: string;
  product_type?: string;
  plans?: PlanCreate[];
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  product_type?: string;
  is_active?: boolean;
}

export const productsApi = {
  // --- PRODUCTS ---
  list: async (activeOnly = true): Promise<Product[]> => {
    const { data } = await apiClient.get("/products/", {
      params: { active_only: activeOnly }
    });
    return data;
  },
  
  get: async (id: string): Promise<Product> => {
    const { data } = await apiClient.get(`/products/${id}`);
    return data;
  },

  create: async (payload: ProductCreate): Promise<Product> => {
    const { data } = await apiClient.post("/products/", payload);
    return data;
  },

  update: async (id: string, payload: ProductUpdate): Promise<Product> => {
    const { data } = await apiClient.patch(`/products/${id}`, payload);
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/products/${id}`);
  },

  // --- PLANS ---
  createPlan: async (productId: string, payload: PlanCreate): Promise<any> => {
    const { data } = await apiClient.post(`/products/${productId}/plans`, payload);
    return data;
  },

  updatePlan: async (planId: string, payload: Partial<PlanCreate> & { is_active?: boolean }): Promise<any> => {
    const { data } = await apiClient.patch(`/plans/${planId}`, payload);
    return data;
  },

  deletePlan: async (planId: string): Promise<void> => {
    await apiClient.delete(`/plans/${planId}`);
  },

  // --- VERSIONS & CALCULATOR ---
  createVersion: async (planId: string, payload: PlanVersionCreate): Promise<any> => {
    const { data } = await apiClient.post(`/plans/${planId}/versions`, payload);
    return data;
  },

  calculatePrice: async (params: PriceCalculationRequest): Promise<PriceCalculationResponse> => {
    const { data } = await apiClient.post("/plans/calculate-price", params);
    return data;
  }
};
