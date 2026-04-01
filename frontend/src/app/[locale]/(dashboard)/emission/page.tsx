"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  FilePlus, 
  Users, 
  FileText, 
  Search, 
  ChevronRight, 
  ShieldCheck, 
  Clock, 
  AlertCircle,
  Plus
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmissionAssistant } from "@/components/emission/emission-assistant";
import { emissionApi, type Policy } from "@/lib/api/emission";

export default function EmissionPage() {
  const [activeTab, setActiveTab] = useState("active");
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);

  const { data: policies, isLoading } = useQuery({
    queryKey: ["policies", activeTab],
    queryFn: () => emissionApi.listPolicies({ status: activeTab.toUpperCase() }),
  });

  const { data: stats } = useQuery({
    queryKey: ["emission-stats"],
    queryFn: () => emissionApi.getStats(),
  });

  if (isAssistantOpen) {
    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => setIsAssistantOpen(false)}>
            Volver
          </Button>
          <h1 className="text-xl font-bold flex items-center gap-2">
            <FilePlus className="w-5 h-5 text-primary-600" /> Nuevo Proceso de Emisión
          </h1>
        </div>
        <EmissionAssistant onComplete={() => setIsAssistantOpen(false)} />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary-200">
              <FilePlus className="w-6 h-6" />
            </div>
             Motor de Emisión
          </h1>
          <p className="text-neutral-500 mt-2">
            Emisión de pólizas individuales, masivas y gestión de vida del contrato.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-11 border-neutral-200 bg-white">
            <Users className="w-4 h-4 mr-2" />
            Carga Masiva (Excel)
          </Button>
          <Button className="h-11 bg-primary-600 hover:bg-primary-700 text-white shadow-md" onClick={() => setIsAssistantOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Nueva Emisión Individual
          </Button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-white">
            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Pendientes de Pago</p>
            <div className="flex items-end justify-between mt-2">
                <span className="text-2xl font-black text-amber-600">{stats?.pending_payment_count ?? 0}</span>
                <Clock className="w-5 h-5 text-amber-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-white font-sans">
            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Activas (Mes)</p>
            <div className="flex items-end justify-between mt-2 text-indigo-900">
                <span className="text-2xl font-black">{stats?.active_count ?? 0}</span>
                <ShieldCheck className="w-5 h-5 text-indigo-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-white">
            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Siniestros Reportados</p>
            <div className="flex items-end justify-between mt-2 text-red-900">
                <span className="text-2xl font-black">{stats?.claims_count ?? 0}</span>
                <AlertCircle className="w-5 h-5 text-red-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-primary-600 text-white">
            <p className="text-[10px] font-bold opacity-80 uppercase tracking-widest">Retention Rate</p>
            <div className="flex items-end justify-between mt-2">
                <span className="text-2xl font-black">{stats?.retention_rate ?? 0}%</span>
                <div className="w-5 h-5 bg-white/20 rounded-full flex items-center justify-center text-[10px]">↗</div>
            </div>
        </GlassCard>
      </div>

      {/* Search & Tabs */}
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full md:w-auto">
                <TabsList className="bg-neutral-100 p-1 rounded-xl h-12">
                    <TabsTrigger value="active" className="rounded-lg px-6 data-[state=active]:bg-white data-[state=active]:shadow-sm">Activas</TabsTrigger>
                    <TabsTrigger value="pending" className="rounded-lg px-6 data-[state=active]:bg-white data-[state=active]:shadow-sm">Pendientes</TabsTrigger>
                    <TabsTrigger value="cancelled" className="rounded-lg px-6 data-[state=active]:bg-white data-[state=active]:shadow-sm">Anuladas</TabsTrigger>
                </TabsList>
            </Tabs>
            
            <div className="relative w-full md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                <Input placeholder="Buscar por DNI, Nombre o Póliza..." className="pl-10 h-12 bg-white border-neutral-200 rounded-xl" />
            </div>
        </div>

        {/* Empty State / List */}
        {isLoading ? (
          <GlassCard className="border-none shadow-glass bg-white/70 min-h-[400px] flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </GlassCard>
        ) : policies && policies.length > 0 ? (
          <GlassCard className="border-none shadow-glass bg-white/70 min-h-[400px] overflow-hidden">
             <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="border-b border-neutral-100 bg-neutral-50/50">
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400">Póliza</th>
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400">Titular</th>
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400">Plan</th>
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400">Estado</th>
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400">Premium</th>
                            <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-neutral-400"></th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-100">
                        {(policies as Policy[]).map((policy) => (
                            <tr key={policy.id} className="hover:bg-neutral-50/50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="flex flex-col">
                                        <span className="font-bold text-neutral-900">{policy.policy_number}</span>
                                        <span className="text-[10px] text-neutral-400">Ene 14, 2024</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-sm font-medium text-neutral-600">{policy.client_name}</td>
                                <td className="px-6 py-4">
                                    <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-100 text-[10px] uppercase font-bold">
                                        {policy.plan_name}
                                    </Badge>
                                </td>
                                <td className="px-6 py-4">
                                    <Badge className={cn(
                                        "text-[10px] uppercase font-bold",
                                        policy.status === "ACTIVE" ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-100" : 
                                        policy.status === "PENDING" ? "bg-amber-100 text-amber-700 hover:bg-amber-100" :
                                        "bg-neutral-100 text-neutral-700 hover:bg-neutral-100"
                                    )}>
                                        {policy.status === "ACTIVE" ? "Activa" : policy.status === "PENDING" ? "Pendiente" : "Anulada"}
                                    </Badge>
                                </td>
                                <td className="px-6 py-4 font-mono text-sm font-bold text-neutral-900">${policy.premium_amount}</td>
                                <td className="px-6 py-4 text-right">
                                    <Button variant="ghost" size="sm" className="text-neutral-400 hover:text-primary-600">
                                        <ChevronRight className="w-4 h-4" />
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
             </div>
          </GlassCard>
        ) : (
          <GlassCard className="border-none shadow-glass bg-white/70 min-h-[400px] flex flex-col items-center justify-center text-center p-12">
              <div className="w-20 h-20 bg-neutral-50 rounded-3xl flex items-center justify-center mb-6 border border-neutral-100">
                  <FilePlus className="w-10 h-10 text-neutral-300" />
              </div>
              <h3 className="text-xl font-bold text-neutral-900">Comienza a emitir cobertura</h3>
              <p className="text-neutral-500 max-w-sm mt-2">
                  Aún no hay pólizas registradas en este estado. Utiliza el botón de "Nueva Emisión" para registrar un titular y activar un plan.
              </p>
              <Button className="mt-8 bg-primary-600 text-white px-8 rounded-xl h-11" onClick={() => setIsAssistantOpen(true)}>
                  Lanzar Asistente de Emisión
              </Button>
          </GlassCard>
        )}
      </div>
    </div>
  );
}
