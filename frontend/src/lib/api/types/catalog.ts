export type CurrencyCode = 'USD' | 'EUR' | 'MXN' | 'COP' | 'GBP';

// --- NIVEL 5: COBERTURAS ---
export interface Coverage {
  id: string;
  name: string;
  description?: string;
  limit_amount: number;
  is_optional: boolean;
  waiting_period_days: number;
}

// --- NIVEL 4: RECARGOS Y PAÍSES ---
export interface AgeSurcharge {
  id: string;
  min_age: number;
  max_age: number;
  surcharge_percentage: number;
}

export interface PlanCountry {
  country_code: string;
  is_available: boolean;
  override_price?: number;
}

// --- NIVEL 3: VERSIONES DE PLAN ---
export interface PlanVersion {
  id: string;
  version_number: number;
  is_active: boolean;
  cost_price: number;
  public_price: number;
  currency: CurrencyCode;
  max_entry_age: number;
  max_renewal_age: number;
  
  // Tiempos de Carencia (Waiting Times)
  wtime_suicide: number;
  wtime_accident: number;
  wtime_preexisting: number;
  
  coverages: Coverage[];
  age_surcharges: AgeSurcharge[];
  countries: PlanCountry[];
  
  created_at: string;
  updated_at: string;
}

// --- NIVEL 2: PLANES ---
export interface Plan {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  company_id?: string;
  versions: PlanVersion[];
}

// --- NIVEL 1: PRODUCTO (RAÍZ) ---
export interface Product {
  id: string;
  name: string;
  description?: string;
  product_type: string;
  is_active: boolean;
  plans: Plan[];
  created_at: string;
  updated_at: string;
}

// --- CALCULADORA ACTUARIAL ---
export interface PriceCalculationRequest {
  plan_version_id: string;
  age: number;
  country_code: string;
  quantity: number;
}

export interface PriceCalculationResponse {
  final_price: number;
  base_price: number;
  country_override?: number;
  age_surcharge_percentage: number;
  age_surcharge_amount: number;
  currency: CurrencyCode;
  breakdown: Record<string, any>;
}
