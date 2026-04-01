"use client";

import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { DollarSign, BadgeDollarSign, CreditCard, ArrowUpRight, TrendingUp } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { financeApi, Transaction } from "@/lib/api/modules";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { ResellerFinancialPanel } from "@/components/finance/reseller-financial-panel";

export default function FinancePage() {
  const t = useTranslations("dashboard");
  const { data: currencies, isLoading: isCurrenciesLoading } = useQuery({
    queryKey: ["currencies"],
    queryFn: financeApi.currencies,
  });

  const { data: transactions, isLoading: isTxLoading } = useQuery({
    queryKey: ["transactions"],
    queryFn: financeApi.transactions,
  });

  // Calculate real summaries based on transactions
  const totalPrimas = transactions?.filter(tx => tx.status === 'PAID').reduce((sum, tx) => sum + tx.amount, 0) || 0;
  const pendingCommissions = totalPrimas * 0.085; // Simulating business logic calculation logic
  const stripeBalance = totalPrimas * 0.90; // Just as estimation for the UI before Stripe balance API integration

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
            Gestión Financiera
          </h1>
          <p className="text-[var(--color-neutral-500)] mt-1">
            Monitorea ingresos, comisiones y configuración de monedas
          </p>
        </div>
      </div>

      <ResellerFinancialPanel />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <GlassCard className="p-6 h-40 flex flex-col justify-between bg-[var(--color-primary-500)] text-white border-none shadow-glass-primary">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium opacity-80">Primas Recaudadas</span>
            <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-end gap-2">
            <span className="text-3xl font-bold">
                {isTxLoading ? "..." : `$${totalPrimas.toLocaleString()}`}
            </span>
            <span className="text-xs mb-1 bg-white/20 px-2 py-0.5 rounded-full font-medium">LIVE</span>
          </div>
        </GlassCard>

        <GlassCard className="p-6 h-40 flex flex-col justify-between border-none shadow-glass bg-white/80 transition-transform group hover:scale-[1.02]">
           <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-neutral-500">Estimación Comisiones</span>
            <div className="w-8 h-8 bg-info-100/50 rounded-lg flex items-center justify-center text-info-600">
              <BadgeDollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-end gap-2 text-neutral-900">
            <span className="text-3xl font-bold">
                {isTxLoading ? "..." : `$${pendingCommissions.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
            </span>
            <span className="text-xs mb-1 text-info-600 font-medium">Auto-Split (8.5%)</span>
          </div>
        </GlassCard>

        <GlassCard className="p-6 h-40 flex flex-col justify-between border-none shadow-glass bg-white/80 transition-transform group hover:scale-[1.02]">
           <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-neutral-500">Saldo Stripe Connect</span>
            <div className="w-8 h-8 bg-primary-100/50 rounded-lg flex items-center justify-center text-primary-600">
              <CreditCard className="w-5 h-5" />
            </div>
          </div>
          <div className="flex items-end gap-2 text-neutral-900">
            <span className="text-3xl font-bold">
                {isTxLoading ? "..." : `$${stripeBalance.toLocaleString()}`}
            </span>
            <ArrowUpRight className="w-5 h-5 text-primary-500" />
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <GlassCard className="p-6 h-[400px] border-none shadow-glass">
          <h3 className="text-lg font-bold text-neutral-900 mb-6">Configuración de Monedas</h3>
          <div className="space-y-4 overflow-y-auto pr-2">
            {isCurrenciesLoading ? (
              Array.from({ length: 2 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full rounded-xl" />
              ))
            ) : currencies?.length > 0 ? (
              currencies.map((curr: any) => (
                <div key={curr.id} className="flex items-center justify-between p-4 bg-neutral-50/50 rounded-xl border border-neutral-100 group hover:border-primary-200 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center font-bold text-primary-600 shadow-sm">
                      {curr.symbol || "$"}
                    </div>
                    <div>
                      <p className="font-bold text-neutral-900">{curr.name}</p>
                      <p className="text-xs text-neutral-500">{curr.code}</p>
                    </div>
                  </div>
                  <Badge variant="outline" className="border-success text-success bg-success-50/20">Activa</Badge>
                </div>
              ))
            ) : (
                <div className="h-full flex flex-col items-center justify-center text-center">
                    <DollarSign className="w-12 h-12 text-neutral-200 mb-2" />
                    <p className="text-neutral-500 text-sm">No se han configurado monedas.</p>
                </div>
            )}
          </div>
        </GlassCard>

        <GlassCard className="p-6 h-[400px] border-none shadow-glass flex flex-col">
          <h3 className="text-lg font-bold text-neutral-900 mb-6 font-sans">Movimientos Recientes</h3>
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
            {isTxLoading ? (
               Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full rounded-xl" />
              ))
            ) : transactions && transactions.length > 0 ? (
              transactions.map((tx: any) => (
                 <div key={tx.id} className="flex items-center justify-between p-4 bg-white/50 border border-neutral-100 rounded-xl hover:border-primary-100 transition-colors">
                    <div className="flex items-center gap-4">
                        <div className={cn(
                            "w-10 h-10 rounded-lg flex items-center justify-center",
                            tx.status === 'PAID' ? "bg-success-100 text-success-600" : "bg-warning-100 text-warning-600"
                        )}>
                            <TrendingUp className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-sm font-bold text-neutral-900">Cobro Póliza {tx.policy_id.split('-')[0]}</p>
                            <p className="text-[10px] text-neutral-500">{new Date(tx.created_at).toLocaleString()}</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-sm font-bold text-neutral-900">${tx.amount.toLocaleString()}</p>
                        <Badge className={cn(
                            "text-[10px] h-5 border-none",
                            tx.status === 'PAID' ? "bg-success-50 text-success-700" : "bg-amber-50 text-amber-700"
                        )}>
                            {tx.status}
                        </Badge>
                    </div>
                 </div>
              ))
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center py-10">
                <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mb-4">
                  <TrendingUp className="w-8 h-8 text-neutral-300" />
                </div>
                <h4 className="text-lg font-bold text-neutral-900">Sin movimientos financieros</h4>
                <p className="text-sm text-neutral-500 max-w-[280px] mt-2">
                  Las transacciones de primas aparecerán aquí una vez que comiences a operar.
                </p>
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
