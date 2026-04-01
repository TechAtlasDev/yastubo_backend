"use client";

import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { History, Search, FileDown, ShieldAlert } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function AuditPage() {
  const t = useTranslations("dashboard");

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
            Auditoría y Trazabilidad
          </h1>
          <p className="text-[var(--color-neutral-500)] mt-1">
            Registro histórico de cada acción y cambio dentro del sistema
          </p>
        </div>
        <div className="flex gap-4">
             <div className="relative group/search">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within/search:text-primary-500 transition-colors" />
                <Input placeholder="Buscar evento..." className="pl-10 h-11 w-64 bg-white/50 border-neutral-200 focus:border-primary-500" />
            </div>
            <button className="h-11 px-5 rounded-xl border border-neutral-200 bg-white/50 text-neutral-700 font-medium flex items-center gap-2 hover:bg-white hover:border-neutral-300 transition-all active:scale-95">
                <FileDown className="w-5 h-5" />
                Exportar CSV
            </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <GlassCard className="p-6 bg-white/80 border-none shadow-glass">
          <p className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-1 font-mono">Eventos Hoy</p>
          <p className="text-3xl font-bold text-neutral-900">1,248</p>
        </GlassCard>
        <GlassCard className="p-6 bg-white/80 border-none shadow-glass">
          <p className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-1 font-mono">Alertas Críticas</p>
          <p className="text-3xl font-bold text-error">0</p>
        </GlassCard>
        <GlassCard className="p-6 bg-white/80 border-none shadow-glass">
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-1 font-mono">Sesiones Activas</p>
            <p className="text-3xl font-bold text-info">12</p>
        </GlassCard>
        <GlassCard className="p-6 bg-white/80 border-none shadow-glass border-l-4 border-l-primary-500">
            <p className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-1 font-mono">Última Accion</p>
            <p className="text-sm font-bold text-neutral-900 mt-2 truncate">Update company configuration: "Atlas Co."</p>
        </GlassCard>
      </div>

      <GlassCard className="overflow-hidden border-none shadow-glass min-h-[400px]">
        <Table>
          <TableHeader className="bg-neutral-50/50">
            <TableRow className="border-none hover:bg-transparent">
              <TableHead className="w-[180px]">Timestamp</TableHead>
              <TableHead>Agente</TableHead>
              <TableHead>Módulo</TableHead>
              <TableHead>Acción</TableHead>
              <TableHead>Entidad ID</TableHead>
              <TableHead className="text-right">Detalles</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
             <TableRow className="border-none opacity-40">
                <TableCell className="font-mono text-xs">2026-03-31 14:24:55</TableCell>
                <TableCell>
                    <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center text-[10px] text-primary-700 font-bold">SY</div>
                        <span className="text-sm font-medium">System Admin</span>
                    </div>
                </TableCell>
                <TableCell><Badge variant="outline">AUTH</Badge></TableCell>
                <TableCell><span className="text-sm font-medium">LOGIN_SUCCESS</span></TableCell>
                <TableCell className="font-mono text-[10px] text-neutral-400">auth-882-xa1</TableCell>
                <TableCell className="text-right"><button className="text-xs text-primary-500 font-bold hover:underline">Ver JSON</button></TableCell>
             </TableRow>
             <TableRow>
                <TableCell colSpan={6} className="h-64 text-center">
                    <div className="flex flex-col items-center justify-center text-neutral-300">
                        <History className="w-12 h-12 mb-4 opacity-10" />
                        <p className="text-sm">Fin del registro histórico.</p>
                    </div>
                </TableCell>
             </TableRow>
          </TableBody>
        </Table>
      </GlassCard>
    </div>
  );
}
