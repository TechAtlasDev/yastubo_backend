"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PaymentGateway } from "@/components/finance/payment-gateway";
import { productsApi } from "@/lib/api/modules";
import { useQuery } from "@tanstack/react-query";
import { Loader2, Plus } from "lucide-react";

export function EmissionAssistant({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(1);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  
  // Simulated created policy ID - in a real app this comes from submitting the form in Step 2
  const [createdPolicyId, setCreatedPolicyId] = useState<string | null>(null);

  const { data: products, isLoading } = useQuery({
    queryKey: ["products", "active"],
    queryFn: () => productsApi.list(true),
  });

  const handleNextStep = () => setStep((s) => s + 1);

  if (step === 1) {
    return (
      <div className="space-y-6 max-w-2xl mx-auto p-4 md:p-6 bg-white rounded-xl shadow-sm border">
        <div>
          <h2 className="text-xl font-bold text-neutral-900">Paso 1: Seleccione el Producto</h2>
          <p className="text-sm text-neutral-500">Elija un plan base para la nueva póliza.</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-primary-500" /></div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {products?.map((p) => (
              <GlassCard
                key={p.id}
                className={`p-4 cursor-pointer transition-all border-2 ${
                  selectedProduct === p.id ? "border-primary-500 bg-primary-50" : "border-transparent hover:border-neutral-200"
                }`}
                onClick={() => setSelectedProduct(p.id)}
              >
                <div className="font-semibold text-lg">{p.name}</div>
                <div className="text-sm text-neutral-500 mt-1 line-clamp-2">{p.description}</div>
                <div className="mt-3 text-xs text-primary-700 font-medium">
                  {p.plans.length} plan(es) disponible(s)
                </div>
              </GlassCard>
            ))}
          </div>
        )}

        <div className="flex justify-end pt-4">
          <Button onClick={handleNextStep} disabled={!selectedProduct}>
            Continuar al Paso 2
          </Button>
        </div>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div className="space-y-6 max-w-2xl mx-auto p-4 md:p-6 bg-white rounded-xl shadow-sm border">
        <div>
          <h2 className="text-xl font-bold text-neutral-900">Paso 2: Datos del Titular</h2>
          <p className="text-sm text-neutral-500">Ingrese la información del titular de la póliza.</p>
        </div>
        
        <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="text-sm font-medium">Nombre</label>
                    <input type="text" className="w-full mt-1 p-2 border rounded-md" defaultValue="Juan" />
                </div>
                <div>
                    <label className="text-sm font-medium">Apellido</label>
                    <input type="text" className="w-full mt-1 p-2 border rounded-md" defaultValue="Pérez" />
                </div>
            </div>
            <div>
                <label className="text-sm font-medium">Correo Electrónico</label>
                <input type="email" className="w-full mt-1 p-2 border rounded-md" defaultValue="juan@ejemplo.com" />
            </div>
            <div>
                <label className="text-sm font-medium">DNI / Pasaporte</label>
                <input type="text" className="w-full mt-1 p-2 border rounded-md" defaultValue="123456789" />
            </div>
        </div>

        <div className="flex justify-between pt-4">
          <Button variant="outline" onClick={() => setStep(1)}>Atrás</Button>
          <Button onClick={() => {
              // Simulating API call to create policy, returning a fake UUID for payment step
              setCreatedPolicyId("6a84c8a2-2cf4-4b6d-a131-15fe9e6f2cb0"); // Use a valid UUID format
              setStep(3);
          }}>
            Guardar y Pagar
          </Button>
        </div>
      </div>
    );
  }

  if (step === 3 && createdPolicyId) {
    return (
      <div className="space-y-6 max-w-2xl mx-auto">
         <div>
          <h2 className="text-xl font-bold text-neutral-900 mb-2">Paso 3: Pago Seguro</h2>
          <p className="text-sm text-neutral-500 mb-6">Complete la información de pago para emitir la póliza.</p>
        </div>
        
        <PaymentGateway 
          policyId={createdPolicyId} 
          onSuccess={() => {
             setStep(4);
          }}
          onCancel={() => setStep(2)}
        />
      </div>
    );
  }

  if (step === 4) {
      return (
        <div className="space-y-6 max-w-2xl mx-auto p-8 text-center bg-white rounded-xl shadow-sm border">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold text-neutral-900">¡Póliza Emitida con Éxito!</h2>
            <p className="text-neutral-500">El pago se ha procesado correctamente y la póliza está ahora activa.</p>
            <Button onClick={onComplete} className="mt-6">Finalizar y volver al inicio</Button>
        </div>
      )
  }

  return null;
}
