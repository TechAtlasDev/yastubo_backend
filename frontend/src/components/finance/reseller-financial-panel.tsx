"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { financeApi } from "@/lib/api/modules";
import { 
  Building2, 
  ExternalLink, 
  ShieldCheck, 
  ShieldAlert, 
  CreditCard, 
  Banknote,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export function ResellerFinancialPanel() {
  const { data: status, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ["stripe-status"],
    queryFn: () => financeApi.getConnectStatus(),
    retry: 1
  });

  const onboardingMutation = useMutation({
    mutationFn: () => financeApi.onboardingUrl(),
    onSuccess: (data: { url: string }) => {
      window.open(data.url, '_blank');
    },
    onError: (error: any) => {
      toast.error("No se pudo generar el enlace: " + error.message);
    }
  });

  const dashboardMutation = useMutation({
    mutationFn: () => financeApi.dashboardUrl(),
    onSuccess: (data: { url: string }) => {
      window.open(data.url, '_blank');
    },
    onError: (error: any) => {
      toast.error("No se pudo generar el enlace al dashboard: " + error.message);
    }
  });

  if (isLoading) {
    return <Skeleton className="h-[200px] w-full rounded-3xl" />;
  }

  const isReady = status?.onboarding_complete && status?.charges_enabled;

  return (
    <GlassCard className={cn(
      "border-none shadow-sm overflow-hidden bg-white/70 transition-all duration-500",
      isReady ? "ring-2 ring-emerald-500/10" : "ring-2 ring-amber-500/10"
    )}>
      <div className="p-1 bg-neutral-50 flex items-center justify-between px-6 py-3 border-b border-neutral-100">
        <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-neutral-400" />
            <span className="text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Estado de Reseller (Connect)</span>
        </div>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => refetch()} 
          className="h-7 text-[10px] font-bold text-primary-600 hover:text-primary-700 hover:bg-primary-50 px-2"
          disabled={isRefetching}
        >
          <RefreshCw className={cn("w-3 h-3 mr-1", isRefetching && "animate-spin")} />
          ACTUALIZAR
        </Button>
      </div>

      <div className="p-8 flex flex-col lg:flex-row items-center justify-between gap-8">
        <div className="flex items-start gap-6">
          <div className={cn(
            "w-20 h-20 rounded-3xl flex items-center justify-center shadow-lg transition-colors duration-500",
            isReady ? "bg-emerald-600 shadow-emerald-200" : "bg-amber-600 shadow-amber-200"
          )}>
            {isReady ? (
               <ShieldCheck className="w-10 h-10 text-white" />
            ) : (
               <ShieldAlert className="w-10 h-10 text-white animate-pulse" />
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center gap-2">
                <h3 className="text-2xl font-black text-neutral-900">
                    {isReady ? "Cuenta Verificada" : "Acción Requerida"}
                </h3>
                <Badge className={cn(
                    "border-none font-bold text-[10px]",
                    isReady ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"
                )}>
                    {isReady ? "ENABLED" : "PENDING"}
                </Badge>
            </div>
            <p className="text-neutral-500 text-sm max-w-md leading-relaxed">
                {isReady 
                  ? "Tu cuenta de Stripe Connect está totalmente operativa. Puedes emitir pólizas y recibir comisiones automáticamente." 
                  : "Stripe requiere información adicional para habilitar cobros y desembolsos en tu cuenta bancaria."}
            </p>
            
            <div className="flex flex-wrap gap-4 pt-4">
                <StatusIndicator 
                    label="Onboarding" 
                    active={status?.onboarding_complete} 
                    icon={<CheckCircle2 className="w-3.5 h-3.5" />} 
                />
                <StatusIndicator 
                    label="Cobros" 
                    active={status?.charges_enabled} 
                    icon={<CreditCard className="w-3.5 h-3.5" />} 
                />
                <StatusIndicator 
                    label="Payouts" 
                    active={status?.payouts_enabled} 
                    icon={<Banknote className="w-3.5 h-3.5" />} 
                />
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-3 w-full lg:w-auto">
            {!isReady ? (
                <Button 
                  onClick={() => onboardingMutation.mutate()}
                  disabled={onboardingMutation.isPending}
                  className="bg-primary-600 hover:bg-primary-700 text-white font-bold h-12 px-8 rounded-2xl shadow-lg shadow-primary-200"
                >
                    {onboardingMutation.isPending ? "Generando..." : "Completar Onboarding en Stripe"}
                    <ExternalLink className="w-4 h-4 ml-2" />
                </Button>
            ) : (
                <Button 
                    variant="outline"
                    onClick={() => dashboardMutation.mutate()}
                    disabled={dashboardMutation.isPending}
                    className="border-neutral-200 h-12 px-8 rounded-2xl text-neutral-600 font-bold hover:bg-neutral-50"
                >
                    {dashboardMutation.isPending ? "Cargando..." : "Ver Dashboard de Stripe"}
                    <ExternalLink className="w-4 h-4 ml-2" />
                </Button>
            )}
            <p className="text-[10px] text-neutral-400 text-center font-medium">
               Procesado por Stripe Connect • YasTubo Financial Engine
            </p>
        </div>
      </div>
    </GlassCard>
  );
}

function StatusIndicator({ label, active, icon }: { label: string; active?: boolean; icon: any }) {
    return (
        <div className={cn(
            "flex items-center gap-2 px-3 py-1.5 rounded-xl border transition-all",
            active 
                ? "bg-emerald-50 border-emerald-100 text-emerald-700" 
                : "bg-neutral-50 border-neutral-100 text-neutral-400"
        )}>
            {active ? icon : <AlertCircle className="w-3.5 h-3.5" />}
            <span className="text-xs font-bold uppercase tracking-tighter">{label}</span>
        </div>
    )
}
