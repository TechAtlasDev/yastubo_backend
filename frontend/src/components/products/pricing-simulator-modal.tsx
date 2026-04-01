"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { productsApi } from "@/lib/api/modules";
import { PlanVersion, PriceCalculationResponse } from "@/lib/api/types/catalog";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogHeader, 
  DialogTitle,
  DialogFooter
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Calculator, 
  Globe, 
  User, 
  ArrowRight, 
  Loader2, 
  CheckCircle2, 
  ChevronRight,
  Info 
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface PricingSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  version: PlanVersion;
  planName: string;
}

export function PricingSimulatorModal({ isOpen, onClose, version, planName }: PricingSimulatorModalProps) {
  const [formData, setFormData] = useState({
    age: 30,
    country_code: "US",
    quantity: 1
  });

  const mutation = useMutation({
    mutationFn: () => productsApi.calculatePrice({
      plan_version_id: version.id,
      age: formData.age,
      country_code: formData.country_code,
      quantity: formData.quantity
    }),
  });

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate();
  };

  const resetAndClose = () => {
    mutation.reset();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={resetAndClose}>
      <DialogContent className="sm:max-w-[500px] overflow-hidden border-none shadow-2xl bg-white p-0">
        <div className="bg-primary-600 p-8 text-white relative">
          <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
            <Calculator className="w-32 h-32" />
          </div>
          <DialogHeader className="relative z-10 text-left">
            <div className="flex items-center gap-3 mb-2">
                <Badge className="bg-white/20 text-white border-white/30 backdrop-blur-md">Actuarial Engine</Badge>
                <Badge className="bg-success-400 text-success-950 font-bold">LIVE</Badge>
            </div>
            <DialogTitle className="text-2xl font-bold">{planName}</DialogTitle>
            <DialogDescription className="text-primary-100 mt-1">
              Simulador de cotización en tiempo real para versión v{version.version_number}.0
            </DialogDescription>
          </DialogHeader>
        </div>

        <div className="p-8 space-y-8">
          <form id="calc-form" onSubmit={handleCalculate} className="grid grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label className="text-xs font-bold uppercase text-neutral-400 flex items-center gap-2">
                <User className="w-3.5 h-3.5" /> Edad del Titular
              </Label>
              <Input 
                type="number" 
                value={formData.age} 
                onChange={(e) => setFormData({...formData, age: parseInt(e.target.value)})}
                className="h-12 bg-neutral-50 border-neutral-200 focus:ring-2 focus:ring-primary-500/20"
                min={0}
                max={version.max_entry_age}
              />
              <p className="text-[10px] text-neutral-400">Límite: {version.max_entry_age} años</p>
            </div>

            <div className="space-y-2">
              <Label className="text-xs font-bold uppercase text-neutral-400 flex items-center gap-2">
                <Globe className="w-3.5 h-3.5" /> País de Destino
              </Label>
              <select 
                value={formData.country_code}
                onChange={(e) => setFormData({...formData, country_code: e.target.value})}
                className="flex h-12 w-full rounded-md border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {version.countries.filter(c => c.is_available).map(c => (
                    <option key={c.country_code} value={c.country_code}>
                        {c.country_code === 'US' ? 'Estados Unidos (US)' : c.country_code}
                    </option>
                ))}
              </select>
            </div>
          </form>

          {/* Results Area */}
          <div className={cn(
            "rounded-3xl p-6 transition-all duration-500",
            mutation.isSuccess ? "bg-success-50 border border-success-100" : "bg-neutral-50 border border-neutral-100"
          )}>
            {mutation.isPending ? (
              <div className="flex flex-col items-center justify-center py-6 text-neutral-400 animate-pulse">
                <Loader2 className="w-8 h-8 animate-spin mb-2" />
                <p className="text-sm font-medium">Ejecutando reglas actuariales...</p>
              </div>
            ) : mutation.isSuccess ? (
              <div className="space-y-4 animate-in zoom-in-95 duration-300">
                <div className="flex justify-between items-end">
                    <div>
                        <p className="text-xs font-bold text-success-600 uppercase tracking-wider mb-1">Precio Final Calculado</p>
                        <h2 className="text-4xl font-black text-neutral-900">
                            <span className="text-primary-600 text-2xl mr-1 font-bold">{version.currency}</span>
                            {mutation.data.final_price.toLocaleString()}
                        </h2>
                    </div>
                    <CheckCircle2 className="w-10 h-10 text-success-500 mb-1" />
                </div>
                
                <div className="pt-4 border-t border-success-200 grid grid-cols-2 gap-x-8 gap-y-3">
                    <ResultRow label="Precio Base" value={mutation.data.base_price} currency={version.currency} />
                    <ResultRow label="Recargo por Edad" value={mutation.data.age_surcharge_amount} currency={version.currency} highlight />
                    {mutation.data.country_override && (
                        <ResultRow label="Ajuste País" value={mutation.data.country_override - mutation.data.base_price} currency={version.currency} />
                    )}
                </div>
              </div>
            ) : mutation.isError ? (
              <div className="p-4 bg-error-50 text-error-700 rounded-2xl flex items-start gap-3 border border-error-100">
                <Info className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                   <p className="font-bold text-sm">Error de Validación</p>
                   <p className="text-xs opacity-80">{(mutation.error as any).response?.data?.detail || "No se pudo realizar el cálculo con los parámetros proporcionados."}</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-6 text-neutral-400 text-center">
                <Info className="w-8 h-8 mb-2 opacity-20" />
                <p className="text-sm font-medium">Ingresa los datos para obtener<br/>la cotización exacta</p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="p-8 pt-0 flex gap-3">
          <Button variant="ghost" onClick={resetAndClose} className="h-12 border border-neutral-200 rounded-xl">
            Cerrar
          </Button>
          <Button 
            form="calc-form" 
            disabled={mutation.isPending}
            className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-bold h-12 rounded-xl shadow-lg shadow-primary-500/20 shadow-blue-500/20"
          >
            {mutation.isPending ? "Calculando..." : "Calcular Cotización"}
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function ResultRow({ label, value, currency, highlight }: { label: string, value: number, currency: string, highlight?: boolean }) {
    return (
        <div className="flex justify-between items-center text-xs">
            <span className="text-neutral-500 font-medium">{label}</span>
            <span className={cn("font-bold font-mono", highlight ? "text-primary-600" : "text-neutral-700")}>
                {value >= 0 ? '+' : ''}{currency} {value.toLocaleString()}
            </span>
        </div>
    )
}
