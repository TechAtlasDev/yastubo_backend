import { apiClient } from "./client";
import { 
  Product, 
  PriceCalculationRequest, 
  PriceCalculationResponse 
} from "./types/catalog";
import {
  KnowledgeDocument,
  CreateKnowledgeDocument,
} from './types/ai';

// --- TYPES FOR FINANCE & AUDIT ---
export interface Transaction {
  id: string;
  policy_id: string;
  stripe_payment_intent_id?: string;
  stripe_invoice_id?: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'PAID' | 'FAILED' | 'SUCCEEDED';
  payment_type: string;
  processed_at?: string;
  client_secret?: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  action: string;
  user_id: string;
  entity: string;
  entity_id: string;
  ip_address: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface PaginatedAuditResponse {
  items: AuditLog[];
  total: number;
  page: number;
  page_size: number;
}

export const aiApi = {
  listKnowledge: async (): Promise<KnowledgeDocument[]> => {
    const { data } = await apiClient.get('/ai/knowledge');
    return data;
  },
    
  uploadPDF: async (file: File): Promise<KnowledgeDocument> => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await apiClient.post('/ai/knowledge/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return data;
  },

  createDocument: async (payload: CreateKnowledgeDocument): Promise<KnowledgeDocument> => {
    const { data } = await apiClient.post('/ai/knowledge', payload);
    return data;
  },

  deleteDocument: async (id: string): Promise<void> => {
    await apiClient.delete(`/ai/knowledge/${id}`);
  },

  chat: async (message: string, sessionId?: string): Promise<{ response: string; session_id: string }> => {
    const { data } = await apiClient.post('/ai/chat', { message, session_id: sessionId });
    return data;
  },
};

export const productsApi = {
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

  calculatePrice: async (params: PriceCalculationRequest): Promise<PriceCalculationResponse> => {
    const { data } = await apiClient.post("/plans/calculate-price", params);
    return data;
  }
};

export interface StripeConnectStatus {
  is_verified: boolean;
  onboarding_complete: boolean;
  stripe_account_id: string;
  charges_enabled: boolean;
  payouts_enabled: boolean;
  details_submitted: boolean;
}

export const financeApi = {
  currencies: async () => {
    const { data } = await apiClient.get("/finance/currencies");
    return data;
  },
  unitsOfMeasure: async () => {
    const { data } = await apiClient.get("/finance/units-of-measure");
    return data;
  },
  transactions: async (): Promise<Transaction[]> => {
    const { data } = await apiClient.get("/payments/transactions");
    return data;
  },
  onboardingUrl: async (): Promise<{ url: string }> => {
    const { data } = await apiClient.post("/payments/connect/onboarding");
    return data;
  },
  dashboardUrl: async (): Promise<{ url: string }> => {
    const { data } = await apiClient.post("/payments/connect/dashboard");
    return data;
  },
  getConnectStatus: async (): Promise<StripeConnectStatus> => {
    const { data } = await apiClient.get("/payments/connect/status");
    return data;
  },
  createPaymentIntent: async (payload: { policy_id: string; save_payment_method?: boolean }): Promise<Transaction> => {
    const { data } = await apiClient.post("/payments/intent", payload);
    return data;
  },
  createSubscription: async (payload: { 
    policy_id: string; 
    stripe_payment_method_id: string; 
    billing_anchor_day?: number 
  }) => {
    const { data } = await apiClient.post("/payments/subscription", payload);
    return data;
  }
};

export const auditApi = {
  logs: async (params: any): Promise<PaginatedAuditResponse> => {
    const { data } = await apiClient.get("/audit/", { params });
    return data;
  }
};

export const emissionApi = {
  registerClient: async (payload: any) => {
    const { data } = await apiClient.post("/emission/clients", payload);
    return data;
  },
  issuePolicy: async (payload: any) => {
    const { data } = await apiClient.post("/emission/issue", payload);
    return data;
  },
  listPolicies: async (params?: any) => {
    const { data } = await apiClient.get("/emission/policies", { params });
    return data;
  },
  getPolicy: async (id: string) => {
    const { data } = await apiClient.get(`/emission/policies/${id}`);
    return data;
  },
  downloadPDF: async (id: string): Promise<Blob> => {
    const { data } = await apiClient.get(`/emission/policies/${id}/pdf`, {
      responseType: 'blob'
    });
    return data;
  }
};

export const capitadosApi = {
  uploadBatch: async (formData: FormData) => {
    const { data } = await apiClient.post("/capitados/batches/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },
  getBatchStatus: async (id: string) => {
    const { data } = await apiClient.get(`/capitados/batches/${id}`);
    return data;
  },
};
