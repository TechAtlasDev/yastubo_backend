"use client";

import { useCompanies, useBusinessUnits } from "@/hooks/use-organizations";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Plus, Building2, LayoutGrid, Users, Settings, Mail, Phone, MapPin, BadgeCheck, ExternalLink, ChevronRight, Globe, TrendingUp, History, UserPlus } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useParams } from "next/navigation";
import { CreateUnitModal } from "@/components/organizations/create-unit-modal";
import { AuditTimeline } from "@/components/audit/audit-timeline";
import { useState } from "react";

export default function CompanyDetailPage() {
  const { id } = useParams();
  const [isUnitModalOpen, setIsUnitModalOpen] = useState(false);
  const { data: companies, isLoading: isCompanyLoading } = useCompanies();
  const { data: units, isLoading: isUnitsLoading } = useBusinessUnits(id as string);

  const company = companies?.find((c: any) => c.id === id);

  if (isCompanyLoading) {
    return (
      <div className="space-y-8 animate-pulse">
        <Skeleton className="h-40 w-full rounded-2xl" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    );
  }

  if (!company) {
    return (
        <div className="h-[60vh] flex flex-col items-center justify-center text-center">
            <Building2 className="w-16 h-16 text-neutral-200 mb-4" />
            <h1 className="text-2xl font-bold text-neutral-900">Empresa no encontrada</h1>
            <p className="text-neutral-500">El ID proporcionado no corresponde a ninguna empresa registrada.</p>
        </div>
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header Profile */}
      <div className="relative overflow-hidden rounded-3xl bg-primary-600 text-white p-8 lg:p-12 shadow-2xl">
        <div className="absolute top-0 right-0 p-8 opacity-10 blur-xl scale-150 rotate-12">
            <Building2 className="w-64 h-64" />
        </div>
        <div className="relative z-10 flex flex-col lg:flex-row gap-8 items-start lg:items-center">
            <div className="w-24 h-24 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 text-white font-bold text-3xl shadow-lg ring-8 ring-white/10">
                {company.name.charAt(0)}
            </div>
            <div className="flex-1 space-y-4">
                <div className="flex flex-wrap items-center gap-3">
                    <h1 className="text-4xl font-bold tracking-tight">{company.name}</h1>
                    <Badge className="bg-success-500/20 text-success-100 border-success-400/50 backdrop-blur-sm px-3 py-1">
                        <BadgeCheck className="w-3.5 h-3.5 mr-1.5" />
                        Verificada
                    </Badge>
                </div>
                <div className="flex flex-wrap gap-x-8 gap-y-3 opacity-90 text-sm font-medium">
                    <div className="flex items-center gap-2"><MapPin className="w-4 h-4 text-primary-200" /> {company.address || "Dirección no especificada"}</div>
                    <div className="flex items-center gap-2"><Mail className="w-4 h-4 text-primary-200" /> {company.email || "Sin email"}</div>
                    <div className="flex items-center gap-2"><Phone className="w-4 h-4 text-primary-200" /> {company.phone || "Sin teléfono"}</div>
                    <div className="flex items-center gap-2"><Globe className="w-4 h-4 text-primary-200" /> yastubo.com</div>
                </div>
            </div>
            <div className="flex gap-4 self-end lg:self-center">
                <Button variant="outline" className="bg-white/10 hover:bg-white/20 border-white/30 text-white backdrop-blur-sm h-12 px-6">
                    <Settings className="w-5 h-5 mr-2" />
                    Editar Perfil
                </Button>
            </div>
        </div>
      </div>

      <Tabs defaultValue="units" className="w-full">
        <TabsList className="bg-white/60 p-1.5 rounded-2xl border border-neutral-200 backdrop-blur-md mb-8 h-14 w-full lg:w-fit">
            <TabsTrigger value="units" className="rounded-xl px-8 h-full data-[state=active]:bg-primary-500 data-[state=active]:text-white font-bold transition-all flex gap-2">
                <LayoutGrid className="w-4 h-4" /> Unidades de Negocio
            </TabsTrigger>
            <TabsTrigger value="finance" className="rounded-xl px-8 h-full data-[state=active]:bg-primary-500 data-[state=active]:text-white font-bold transition-all flex gap-2">
                <TrendingUp className="w-4 h-4" /> Comisiones
            </TabsTrigger>
            <TabsTrigger value="users" className="rounded-xl px-8 h-full data-[state=active]:bg-primary-500 data-[state=active]:text-white font-bold transition-all flex gap-2">
                <Users className="w-4 h-4" /> Staff
            </TabsTrigger>
            <TabsTrigger value="history" className="rounded-xl px-8 h-full data-[state=active]:bg-primary-500 data-[state=active]:text-white font-bold transition-all flex gap-2">
                <History className="w-4 h-4" /> Auditoría
            </TabsTrigger>
        </TabsList>

        <TabsContent value="units" className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-neutral-900">Oficinas y Agencias</h2>
                    <p className="text-neutral-500">Unidades operativas autorizadas bajo {company.name}</p>
                </div>
                <Button 
                    onClick={() => setIsUnitModalOpen(true)}
                    className="bg-primary-500 hover:bg-primary-600 text-white font-bold h-11 px-6 shadow-lg shadow-primary-500/20"
                >
                    <Plus className="w-5 h-5 mr-2" /> Nueva Unidad
                </Button>
            </div>

            <CreateUnitModal companyId={id as string} isOpen={isUnitModalOpen} onClose={() => setIsUnitModalOpen(false)} />

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {isUnitsLoading ? (
                    Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-64 w-full rounded-3xl" />)
                ) : units && units.length > 0 ? (
                    units.map((unit: any) => (
                        <GlassCard key={unit.id} className="p-8 border-none shadow-glass bg-white group hover:scale-[1.02] transition-all cursor-pointer">
                            <div className="flex justify-between items-start mb-6">
                                <div className="w-14 h-14 bg-info-50 rounded-2xl flex items-center justify-center text-info-600 border border-info-100 group-hover:bg-info-500 group-hover:text-white transition-colors duration-300">
                                    <LayoutGrid className="w-7 h-7" />
                                </div>
                                <Badge className="bg-neutral-100 text-neutral-600 border-none group-hover:bg-info-100 group-hover:text-info-700 transition-colors">
                                    {unit.type || "Sucursal"}
                                </Badge>
                            </div>
                            <h3 className="text-xl font-bold text-neutral-900 mb-2 truncate">{unit.name}</h3>
                            <div className="space-y-3 mb-8">
                                <p className="text-sm text-neutral-500 flex items-center gap-2"><MapPin className="w-4 h-4 opacity-50" /> {unit.city || "Ciudad Principal"}</p>
                                <p className="text-sm text-neutral-500 flex items-center gap-2"><Users className="w-4 h-4 opacity-50" /> 12 Colaboradores</p>
                            </div>
                            <div className="flex items-center justify-between pt-6 border-t border-neutral-100">
                                <div className="flex -space-x-3">
                                    {Array.from({ length: 3 }).map((_, i) => (
                                        <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-neutral-200 flex items-center justify-center text-[10px] font-bold text-neutral-400 overflow-hidden">
                                            {String.fromCharCode(65 + i)}
                                        </div>
                                    ))}
                                    <div className="w-8 h-8 rounded-full border-2 border-white bg-primary-50 flex items-center justify-center text-[10px] font-bold text-primary-600">+9</div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-neutral-300 group-hover:text-primary-500 group-hover:translate-x-1 transition-all" />
                            </div>
                        </GlassCard>
                    ))
                ) : (
                    <GlassCard className="col-span-full py-20 bg-white/40 border-dashed border-2 border-neutral-200 shadow-none flex flex-col items-center justify-center text-center">
                        <LayoutGrid className="w-16 h-16 text-neutral-200 mb-4" />
                        <h3 className="text-xl font-bold text-neutral-900">No hay unidades</h3>
                        <p className="text-neutral-500 mt-2 max-w-sm">Esta empresa aún no tiene oficinas o agencias registradas.</p>
                        <Button variant="outline" className="mt-6 border-primary-200 text-primary-600 hover:bg-primary-50">Configurar Primera Unidad</Button>
                    </GlassCard>
                )}
            </div>
        </TabsContent>
        <TabsContent value="history" className="space-y-6">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-neutral-900">Historial de Auditoría</h2>
                    <p className="text-neutral-500">Trazabilidad completa de operaciones para {company.name}</p>
                </div>
                <Button variant="outline" className="border-neutral-200 text-neutral-600 bg-white shadow-sm">
                    <History className="w-4 h-4 mr-2" />
                    Descargar Informe
                </Button>
            </div>
            
            <GlassCard className="p-10 border-none shadow-glass bg-white/60">
                <AuditTimeline entityId={id as string} />
            </GlassCard>
        </TabsContent>
      </Tabs>
    </div>
  );
}
