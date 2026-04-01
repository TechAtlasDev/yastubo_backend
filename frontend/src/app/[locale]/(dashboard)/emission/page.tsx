"use client";

import { useState } from "react";
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

export default function EmissionPage() {
  const [activeTab, setActiveTab] = useState("active");

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
          <Button className="h-11 bg-primary-600 hover:bg-primary-700 text-white shadow-md">
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
                <span className="text-2xl font-black text-amber-600">14</span>
                <Clock className="w-5 h-5 text-amber-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-white font-sans">
            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Activas (Mes)</p>
            <div className="flex items-end justify-between mt-2 text-indigo-900">
                <span className="text-2xl font-black">128</span>
                <ShieldCheck className="w-5 h-5 text-indigo-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-white">
            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest">Siniestros Reportados</p>
            <div className="flex items-end justify-between mt-2 text-red-900">
                <span className="text-2xl font-black">2</span>
                <AlertCircle className="w-5 h-5 text-red-200" />
            </div>
        </GlassCard>
        <GlassCard className="p-5 border-none shadow-sm flex flex-col justify-between bg-primary-600 text-white">
            <p className="text-[10px] font-bold opacity-80 uppercase tracking-widest">Retention Rate</p>
            <div className="flex items-end justify-between mt-2">
                <span className="text-2xl font-black">94.2%</span>
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
        <GlassCard className="border-none shadow-glass bg-white/70 min-h-[400px] flex flex-col items-center justify-center text-center p-12">
            <div className="w-20 h-20 bg-neutral-50 rounded-3xl flex items-center justify-center mb-6 border border-neutral-100">
                <FilePlus className="w-10 h-10 text-neutral-300" />
            </div>
            <h3 className="text-xl font-bold text-neutral-900">Comienza a emitir cobertura</h3>
            <p className="text-neutral-500 max-w-sm mt-2">
                Aún no hay pólizas registradas en este estado. Utiliza el botón de "Nueva Emisión" para registrar un titular y activar un plan.
            </p>
            <Button className="mt-8 bg-primary-600 text-white px-8 rounded-xl h-11">
                Lanzar Asistente de Emisión
            </Button>
        </GlassCard>
      </div>
    </div>
  );
}
