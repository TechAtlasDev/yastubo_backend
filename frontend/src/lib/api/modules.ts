import { apiClient } from "./client";

export const productsApi = {
  list: async () => {
    const { data } = await apiClient.get("/products/");
    return data;
  },
  get: async (id: string) => {
    const { data } = await apiClient.get(`/products/${id}`);
    return data;
  },
};

export const financeApi = {
  currencies: async () => {
    const { data } = await apiClient.get("/finance/currencies");
    return data;
  },
  unitsOfMeasure: async () => {
    const { data } = await apiClient.get("/finance/units-of-measure");
    return data;
  },
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
