"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { productsApi } from "@/lib/api/products";
import { emissionApi } from "@/lib/api/emission";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Loader2, 
  ChevronRight, 
  ShieldCheck, 
  CreditCard, 
  CheckCircle2,
  ArrowLeft,
  Package,
  Zap
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PaymentGateway } from "@/components/finance/payment-gateway";

type Step = "PRODUCT" | "CLIENT" | "PAYMENT" | "SUCCESS";

export function EmissionAssistant({ onComplete }: { onComplete: () => void }) {
  const queryClient = useQueryClient();
  const [step, setStep] = useState<Step>("PRODUCT");
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [selectedPlanVersionId, setSelectedPlanVersionId] = useState<string | null>(null);
  const [createdClientId, setCreatedClientId] = useState<string | null>(null);
  const [createdPolicyId, setCreatedPolicyId] = useState<string | null>(null);

  // Form states for client
  const [clientForm, setClientForm] = useState({
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    document_type: "DNI",
    document_number: "",
    birth_date: "1990-01-01",
    nationality: "AR",
    country_of_residence: "AR",
  });

  // 1. Fetch products
  const { data: products, isLoading: isLoadingProducts } = useQuery({
    queryKey: ["products", "active"],
    queryFn: () => productsApi.list(true),
  });

  // 2. Mutations
  const registerClientMutation = useMutation({
    mutationFn: (data: any) => emissionApi.registerClient(data),
    onSuccess: (data) => {
      setCreatedClientId(data.id);
      // Automatically issue policy after client registration
      issuePolicyMutation.mutate({
        client_id: data.id,
        plan_version_id: selectedPlanVersionId!,
      });
    },
  });

  const issuePolicyMutation = useMutation({
    mutationFn: (data: any) => emissionApi.issuePolicy(data),
    onSuccess: (data) => {
      setCreatedPolicyId(data.id);
      setStep("PAYMENT");
    },
  });

  const handleClientSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    registerClientMutation.mutate(clientForm);
  };

  const renderProductStep = () => (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-primary-50 text-primary-600 mb-2">
          <Package className="w-6 h-6" />
        </div>
        <h2 className="text-2xl font-bold text-neutral-900">Selecciona el Producto</h2>
        <p className="text-neutral-500">Elige la cobertura base para esta nueva emisión individual.</p>
      </div>

      {isLoadingProducts ? (
        <div className="flex flex-col items-center justify-center p-12 space-y-4">
          <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
          <p className="text-sm text-neutral-400 font-medium">Cargando catálogo de productos...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {products?.map((product) => (
            <GlassCard
              key={product.id}
              onClick={() => {
                setSelectedProduct(product);
                // Auto-select first active plan version if available
                if (product.plans?.[0]?.versions?.[0]) {
                  setSelectedPlanVersionId(product.plans[0].versions[0].id);
                }
              }}
              className={cn(
                "p-6 cursor-pointer transition-all duration-300 group border-2",
                selectedProduct?.id === product.id 
                  ? "border-primary-500 bg-primary-50/50 shadow-lg shadow-primary-100/50" 
                  : "border-neutral-100 hover:border-primary-200 hover:bg-white bg-white"
              )}
            >
              <div className="flex justify-between items-start mb-4">
                <div className={cn(
                  "w-10 h-10 rounded-xl flex items-center justify-center",
                  selectedProduct?.id === product.id ? "bg-primary-600 text-white" : "bg-neutral-100 text-neutral-500"
                )}>
                  <ShieldCheck className="w-5 h-5" />
                </div>
                {selectedProduct?.id === product.id && (
                  <CheckCircle2 className="w-5 h-5 text-primary-600" />
                )}
              </div>
              <h3 className="font-bold text-neutral-900 text-lg group-hover:text-primary-700 transition-colors">
                {product.name}
              </h3>
              <p className="text-sm text-neutral-500 mt-2 line-clamp-2 leading-relaxed">
                {product.description}
              </p>
              <div className="mt-4 pt-4 border-t border-neutral-100 flex items-center justify-between">
                <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest">
                  {product.plans?.length || 0} Variantes
                </span>
                <ChevronRight className={cn(
                  "w-4 h-4 transition-transform",
                  selectedProduct?.id === product.id ? "text-primary-600 translate-x-1" : "text-neutral-300"
                )} />
              </div>
            </GlassCard>
          ))}
        </div>
      )}

      <div className="flex justify-center pt-4">
        <Button 
          size="lg"
          onClick={() => setStep("CLIENT")} 
          disabled={!selectedProduct}
          className="bg-primary-600 hover:bg-primary-700 text-white px-12 rounded-xl h-12 shadow-lg shadow-primary-200"
        >
          Continuar con los Datos <ChevronRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );

  const renderClientStep = () => (
    <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-500 max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-2">
        <Button variant="ghost" size="icon" onClick={() => setStep("PRODUCT")} className="rounded-full">
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">Datos del Titular</h2>
          <p className="text-sm text-neutral-500">Información personal para la generación del certificado.</p>
        </div>
      </div>

      <GlassCard className="p-8 bg-white border-none shadow-glass">
        <form onSubmit={handleClientSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="first_name">Nombre</Label>
              <Input 
                id="first_name"
                required
                value={clientForm.first_name}
                onChange={(e) => setClientForm({...clientForm, first_name: e.target.value})}
                placeholder="Ej. Juan"
                className="h-11 border-neutral-200 rounded-xl"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Apellido</Label>
              <Input 
                id="last_name"
                required
                value={clientForm.last_name}
                onChange={(e) => setClientForm({...clientForm, last_name: e.target.value})}
                placeholder="Ej. Pérez"
                className="h-11 border-neutral-200 rounded-xl"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="email">Email Corporativo / Personal</Label>
              <Input 
                id="email"
                type="email"
                required
                value={clientForm.email}
                onChange={(e) => setClientForm({...clientForm, email: e.target.value})}
                placeholder="juan.perez@empresa.com"
                className="h-11 border-neutral-200 rounded-xl"
              />
            </div>
             <div className="space-y-2">
              <Label htmlFor="document_number">Número de Documento (DNI/Passport)</Label>
              <Input 
                id="document_number"
                required
                value={clientForm.document_number}
                onChange={(e) => setClientForm({...clientForm, document_number: e.target.value})}
                placeholder="12345678"
                className="h-11 border-neutral-200 rounded-xl"
              />
            </div>
          </div>

          <div className="pt-4">
            <Button 
                type="submit"
                disabled={registerClientMutation.isPending || issuePolicyMutation.isPending}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white h-12 rounded-xl shadow-lg shadow-primary-100"
            >
              {(registerClientMutation.isPending || issuePolicyMutation.isPending) ? (
                <> <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Procesando emisión... </>
              ) : (
                <> <Zap className="w-4 h-4 mr-2" /> Confirmar y Proceder al Pago </>
              )}
            </Button>
          </div>
        </form>
      </GlassCard>
    </div>
  );

  const renderPaymentStep = () => (
    <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500 max-w-lg mx-auto">
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 mb-2">
          <CreditCard className="w-6 h-6" />
        </div>
        <h2 className="text-2xl font-bold text-neutral-900">Pasarela de Pago</h2>
        <p className="text-neutral-500">Tu póliza ha sido pre-generada. Por favor completa el pago.</p>
      </div>

      <GlassCard className="p-0 overflow-hidden border-none shadow-glass bg-white">
        <div className="p-6 bg-neutral-900 text-white">
            <div className="flex justify-between items-center opacity-60 text-[10px] uppercase font-bold tracking-widest mb-1">
                <span>Producto Seleccionado</span>
                <span>Referencia de Emisión</span>
            </div>
            <div className="flex justify-between items-center">
                <span className="font-bold text-lg">{selectedProduct?.name}</span>
                <span className="font-mono text-sm opacity-80">{createdPolicyId?.split('-')[0].toUpperCase()}</span>
            </div>
        </div>
        <div className="p-6">
            {createdPolicyId && (
                <PaymentGateway 
                    policyId={createdPolicyId}
                    onSuccess={() => {
                        queryClient.invalidateQueries({ queryKey: ["policies"] });
                        setStep("SUCCESS");
                    }}
                    onCancel={() => setStep("CLIENT")}
                />
            )}
        </div>
      </GlassCard>
    </div>
  );

  const renderSuccessStep = () => (
    <div className="space-y-8 animate-in fade-in zoom-in-95 duration-500 text-center max-w-md mx-auto pt-12">
        <div className="relative">
            <div className="absolute inset-0 bg-emerald-200 blur-3xl opacity-20 rounded-full scale-150"></div>
            <div className="relative w-24 h-24 bg-emerald-500 text-white rounded-[2.5rem] flex items-center justify-center mx-auto shadow-2xl shadow-emerald-200 animate-bounce">
                <CheckCircle2 className="w-12 h-12" />
            </div>
        </div>
        
        <div className="space-y-3">
            <h2 className="text-3xl font-black text-neutral-900">¡Emisión Exitosa!</h2>
            <p className="text-neutral-500">La cobertura ha sido activada y el comprobante enviado al cliente.</p>
        </div>

        <div className="pt-6 space-y-3">
            <Button 
                onClick={onComplete}
                className="w-full bg-neutral-900 hover:bg-black text-white h-12 rounded-xl font-bold"
            >
                Volver al Dashboard
            </Button>
            <Button 
                variant="outline"
                onClick={() => {
                    setStep("PRODUCT");
                    setSelectedProduct(null);
                    setCreatedPolicyId(null);
                }}
                className="w-full border-neutral-200 text-neutral-600 h-12 rounded-xl"
            >
                Emitir Otra Póliza
            </Button>
        </div>
    </div>
  );

  return (
    <div className="min-h-[500px]">
      {step === "PRODUCT" && renderProductStep()}
      {step === "CLIENT" && renderClientStep()}
      {step === "PAYMENT" && renderPaymentStep()}
      {step === "SUCCESS" && renderSuccessStep()}
    </div>
  );
}
