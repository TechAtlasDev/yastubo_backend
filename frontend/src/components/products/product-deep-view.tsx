"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Product, Plan, PlanVersion } from "@/lib/api/types/catalog";
import { productsApi } from "@/lib/api/products";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ChevronRight, 
  ChevronDown, 
  Layers, 
  ShieldCheck, 
  Globe, 
  Clock, 
  Calculator,
  ArrowUpRight,
  Plus,
  Edit2,
  Trash2
} from "lucide-react";
import { cn } from "@/lib/utils";
import { PricingSimulatorModal } from "./pricing-simulator-modal";
import { PlanManager } from "./plan-manager";
import { VersionManager } from "./version-manager";
import { toast } from "sonner";

interface ProductDeepViewProps {
  product: Product;
}

export function ProductDeepView({ product }: ProductDeepViewProps) {
  const queryClient = useQueryClient();
  const [expandedPlan, setExpandedPlan] = useState<string | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<{version: PlanVersion, planName: string} | null>(null);
  const [isPlanManagerOpen, setIsPlanManagerOpen] = useState(false);
  const [isVersionManagerOpen, setIsVersionManagerOpen] = useState(false);
  const [selectedPlanForEdit, setSelectedPlanForEdit] = useState<Plan | undefined>();
  const [selectedVersionForEdit, setSelectedVersionForEdit] = useState<PlanVersion | undefined>();
  const [selectedPlanForVersion, setSelectedPlanForVersion] = useState<string | undefined>();

  const deletePlanMutation = useMutation({
    mutationFn: (planId: string) => productsApi.deletePlan(planId),
    onSuccess: () => {
      toast.success("Plan eliminado exitosamente");
      queryClient.invalidateQueries({ queryKey: ["products"] });
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Error al eliminar plan");
    },
  });

  const handleDeletePlan = async (planId: string) => {
    if (confirm("¿Estás seguro de que deseas eliminar este plan y todas sus versiones?")) {
      await deletePlanMutation.mutateAsync(planId);
    }
  };

  const handleOpenPlanManager = (plan?: Plan) => {
    setSelectedPlanForEdit(plan);
    setIsPlanManagerOpen(true);
  };

  const handleOpenVersionManager = (planId: string, version?: PlanVersion) => {
    setSelectedPlanForVersion(planId);
    setSelectedVersionForEdit(version);
    setIsVersionManagerOpen(true);
  };

  return (
    <div className="space-y-6">
      {selectedVersion && (
        <PricingSimulatorModal 
          isOpen={!!selectedVersion}
          onClose={() => setSelectedVersion(null)}
          version={selectedVersion.version}
          planName={selectedVersion.planName}
        />
      )}

      <PlanManager
        isOpen={isPlanManagerOpen}
        onClose={() => {
          setIsPlanManagerOpen(false);
          setSelectedPlanForEdit(undefined);
        }}
        productId={product.id}
        plan={selectedPlanForEdit}
      />

      {selectedPlanForVersion && (
        <VersionManager
          isOpen={isVersionManagerOpen}
          onClose={() => {
            setIsVersionManagerOpen(false);
            setSelectedVersionForEdit(undefined);
            setSelectedPlanForVersion(undefined);
          }}
          planId={selectedPlanForVersion}
          version={selectedVersionForEdit}
        />
      )}

      <div className="space-y-4">
        {/* Add Plan Button */}
        <Button
          onClick={() => handleOpenPlanManager()}
          className="w-full bg-primary-50 hover:bg-primary-100 text-primary-700 border border-primary-200 h-11 font-semibold"
        >
          <Plus className="w-4 h-4 mr-2" />
          Agregar Nuevo Plan
        </Button>

        {product.plans?.map((plan) => (
          <div key={plan.id} className="group">
            <GlassCard 
              className={cn(
                "p-0 overflow-hidden border-none shadow-sm transition-all duration-300 bg-white/80 hover:shadow-md",
                expandedPlan === plan.id && "ring-2 ring-primary-500/20 shadow-lg"
              )}
            >
              {/* Plan Header */}
              <div 
                className="p-6 flex items-center justify-between cursor-pointer"
                onClick={() => setExpandedPlan(expandedPlan === plan.id ? null : plan.id)}
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "w-10 h-10 rounded-xl flex items-center justify-center transition-colors",
                    expandedPlan === plan.id ? "bg-primary-500 text-white" : "bg-neutral-100 text-neutral-500"
                  )}>
                    <Layers className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-neutral-900">{plan.name}</h4>
                    <p className="text-xs text-neutral-500">{plan.versions?.length || 0} Versiones Actuariales</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                    <Badge variant={plan.is_active ? "default" : "secondary"} className="rounded-full">
                        {plan.is_active ? "Activo" : "Inactivo"}
                    </Badge>
                    {expandedPlan === plan.id ? <ChevronDown className="w-5 h-5 text-neutral-400" /> : <ChevronRight className="w-5 h-5 text-neutral-400" />}
                </div>
              </div>

              {/* Expanded Plan Details (Versions & Config) */}
              {expandedPlan === plan.id && (
                <div className="px-6 pb-6 animate-in slide-in-from-top-2 duration-300">
                  <div className="border-t border-neutral-100 pt-6 space-y-4">
                    {/* Plan Actions */}
                    <div className="flex gap-2 mb-4">
                      <Button
                        onClick={() => handleOpenPlanManager(plan)}
                        size="sm"
                        variant="outline"
                        className="text-neutral-600 border-neutral-200"
                      >
                        <Edit2 className="w-4 h-4 mr-2" />
                        Editar Plan
                      </Button>
                      <Button
                        onClick={() => handleDeletePlan(plan.id)}
                        size="sm"
                        variant="outline"
                        className="text-red-600 border-red-200 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Eliminar
                      </Button>
                      <Button
                        onClick={() => handleOpenVersionManager(plan.id)}
                        size="sm"
                        className="ml-auto bg-primary-500 hover:bg-primary-600 text-white"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Nueva Versión
                      </Button>
                    </div>

                    {/* Versions List */}
                    {plan.versions?.length ? (
                      <div className="space-y-4">
                        {plan.versions.map((version) => (
                          <div key={version.id} className="bg-neutral-50/50 rounded-2xl p-6 border border-neutral-100">
                            <div className="flex flex-col lg:flex-row justify-between gap-6">
                              {/* Version Metadata */}
                              <div className="space-y-4 flex-1">
                                <div className="flex items-center gap-2">
                                    <Badge className="bg-primary-100 text-primary-700 hover:bg-primary-100 border-none font-mono">
                                        v{version.version_number}.0
                                    </Badge>
                                    {version.is_active && (
                                        <Badge className="bg-success-100 text-success-700 hover:bg-success-100 border-none">
                                            En Producción
                                        </Badge>
                                    )}
                                </div>
                                
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <PriceCard label="P. Público" value={version.public_price} currency={version.currency} />
                                    <PriceCard label="P. Costo" value={version.cost_price} currency={version.currency} />
                                    <PriceCard label="Min. Edad" value={0} unit="años" />
                                    <PriceCard label="Max. Entrada" value={version.max_entry_age} unit="años" />
                                </div>
                              </div>

                              {/* Action Bar */}
                              <div className="flex flex-row lg:flex-col gap-2 justify-end lg:justify-start">
                                 <Button 
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      setSelectedVersion({ version, planName: plan.name });
                                    }}
                                    size="sm" 
                                    className="bg-primary-600 hover:bg-primary-700 text-white font-bold h-10 px-4 shadow-sm group/calc"
                                 >
                                    <Calculator className="w-4 h-4 mr-2" />
                                    Cotizar
                                    <ArrowUpRight className="w-3 h-3 ml-1 opacity-0 group-hover/calc:opacity-100 transition-opacity" />
                                 </Button>
                                 <Button variant="outline" size="sm" className="h-10 px-4 border-neutral-200 text-neutral-600">
                                    <ShieldCheck className="w-4 h-4 mr-2" />
                                    Coberturas ({version.coverages?.length || 0})
                                 </Button>
                              </div>
                            </div>

                            {/* Waiting Times & Rules */}
                            <div className="mt-6 flex flex-wrap gap-4 pt-4 border-t border-dashed border-neutral-200">
                                <RuleIcon icon={Clock} label="Carencia Suicidio" value={`${version.wtime_suicide}d`} />
                                <RuleIcon icon={Clock} label="Carencia Accidente" value={`${version.wtime_accident}d`} />
                                <RuleIcon icon={Globe} label="Países Disponibles" value={version.countries?.filter(c => c.is_available).length.toString()} />
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-neutral-500 text-sm mb-4">No hay versiones creadas para este plan</p>
                        <Button
                          onClick={() => handleOpenVersionManager(plan.id)}
                          size="sm"
                          className="bg-primary-500 hover:bg-primary-600 text-white"
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Crear Primera Versión
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </GlassCard>
          </div>
        ))}
      </div>
    </div>
  );
}

function PriceCard({ label, value, currency, unit }: { label: string, value: number, currency?: string, unit?: string }) {
    return (
        <div className="bg-white p-3 rounded-xl border border-neutral-100 shadow-sm">
            <p className="text-[10px] uppercase font-bold text-neutral-400 mb-1">{label}</p>
            <p className="text-sm font-bold text-neutral-900">
                {currency && <span className="mr-1 text-primary-500">{currency}</span>}
                {value.toLocaleString()}
                {unit && <span className="ml-1 text-neutral-400 font-normal">{unit}</span>}
            </p>
        </div>
    )
}

function RuleIcon({ icon: Icon, label, value }: { icon: any, label: string, value: string }) {
    return (
        <div className="flex items-center gap-2 text-xs font-medium text-neutral-500">
            <Icon className="w-3.5 h-3.5 text-neutral-300" />
            <span>{label}:</span>
            <span className="text-neutral-900 font-bold">{value}</span>
        </div>
    )
}
