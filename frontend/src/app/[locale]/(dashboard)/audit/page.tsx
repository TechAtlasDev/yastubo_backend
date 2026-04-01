"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { auditApi } from "@/lib/api/modules";
import { 
  History, 
  Search, 
  Download, 
  ShieldAlert, 
  UserCheck, 
  Clock, 
  Filter,
  Eye,
  Activity,
  ChevronLeft,
  ChevronRight,
  FileDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { AuditLogDetailModal } from "@/components/audit/audit-log-detail-modal";
import { 
    Table, 
    TableBody, 
    TableCell, 
    TableHead, 
    TableHeader, 
    TableRow 
} from "@/components/ui/table";

export default function AuditPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedLog, setSelectedLog] = useState<any>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs", page, search],
    queryFn: () => auditApi.logs({ page, page_size: 15, action: search || undefined }),
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <AuditLogDetailModal 
        isOpen={!!selectedLog} 
        onClose={() => setSelectedLog(null)} 
        log={selectedLog} 
      />
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-neutral-900 flex items-center gap-3">
            <div className="w-10 h-10 bg-neutral-900 rounded-xl flex items-center justify-center text-white shadow-lg">
              <History className="w-6 h-6" />
            </div>
            Auditoría y Trazabilidad
          </h1>
          <p className="text-neutral-500 mt-2">
            Registro histórico de cada acción y cambio dentro del sistema (Forensic Logs).
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-11 border-neutral-200 shadow-sm bg-white">
            <Download className="w-4 h-4 mr-2" />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard 
            icon={<Activity className="w-5 h-5 text-indigo-500" />} 
            label="Eventos Hoy" 
            value={data?.total || 0} 
            color="indigo" 
        />
        <StatCard 
            icon={<ShieldAlert className="w-5 h-5 text-red-500" />} 
            label="Alertas Críticas" 
            value="0" 
            color="red" 
        />
        <StatCard 
            icon={<UserCheck className="w-5 h-5 text-emerald-500" />} 
            label="Sesiones Activas" 
            value="1" 
            color="emerald" 
        />
        <StatCard 
            icon={<Clock className="w-5 h-5 text-amber-500" />} 
            label="Uptime Promedio" 
            value="99.9%" 
            color="amber" 
        />
      </div>

      {/* Main Table Area */}
      <GlassCard className="border-none shadow-glass overflow-hidden bg-white/70">
        <div className="p-6 border-b border-neutral-100/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <Input 
                placeholder="Buscar por acción (ej: POLICY_CREATED)..." 
                className="pl-10 h-11 bg-white/50 border-neutral-200 rounded-xl focus:ring-primary-500/10"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" className="text-neutral-500">
                <Filter className="w-4 h-4 mr-2" />
                Filtros Avanzados
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-neutral-50/50">
              <TableRow className="hover:bg-transparent border-neutral-100">
                <TableHead className="font-bold text-neutral-900">Timestamp</TableHead>
                <TableHead className="font-bold text-neutral-900">Agente (ID)</TableHead>
                <TableHead className="font-bold text-neutral-900">Acción</TableHead>
                <TableHead className="font-bold text-neutral-900">Entidad</TableHead>
                <TableHead className="font-bold text-neutral-900">IP</TableHead>
                <TableHead className="text-right font-bold text-neutral-900">Detalles</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                        <TableCell colSpan={6}><Skeleton className="h-12 w-full" /></TableCell>
                    </TableRow>
                ))
              ) : data?.items.map((log: any) => (
                <TableRow key={log.id} className="group hover:bg-neutral-50/50 transition-colors border-neutral-50">
                  <TableCell className="text-xs font-medium text-neutral-500">
                    {new Date(log.created_at).toLocaleString('es-ES', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    })}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-lg bg-neutral-100 flex items-center justify-center text-[10px] font-bold text-neutral-500">
                            {log.user_id?.split('-')[0].toUpperCase() || 'SYS'}
                        </div>
                        <span className="text-xs font-mono text-neutral-400">
                            {log.user_id?.split('-')[0]}...
                        </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={cn(
                        "font-mono text-[10px] py-0 h-5 border-none",
                        getActionColor(log.action)
                    )}>
                        {log.action}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs font-bold text-neutral-700">
                    {log.entity}
                  </TableCell>
                  <TableCell className="text-xs text-neutral-400 font-mono">
                    {log.ip_address || "127.0.0.1"}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      onClick={() => setSelectedLog(log)}
                      className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity bg-neutral-100/50 hover:bg-primary-50 hover:text-primary-600"
                    >
                        <Eye className="w-4 h-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-neutral-100 flex items-center justify-between">
            <p className="text-xs text-neutral-500">
                Mostrando <span className="font-bold text-neutral-900">{data?.items.length || 0}</span> de <span className="font-bold text-neutral-900">{data?.total || 0}</span> eventos
            </p>
            <div className="flex items-center gap-1">
                <Button 
                    variant="outline" 
                    size="icon" 
                    className="h-8 w-8 rounded-lg"
                    disabled={page === 1}
                    onClick={() => setPage(p => p - 1)}
                >
                    <ChevronLeft className="w-4 h-4" />
                </Button>
                <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center text-xs font-bold text-primary-600">
                    {page}
                </div>
                <Button 
                    variant="outline" 
                    size="icon" 
                    className="h-8 w-8 rounded-lg"
                    disabled={!data || data.items.length < 15}
                    onClick={() => setPage(p => p + 1)}
                >
                    <ChevronRight className="w-4 h-4" />
                </Button>
            </div>
        </div>
      </GlassCard>
    </div>
  );
}

function StatCard({ icon, label, value, color }: any) {
    const colors: any = {
        indigo: "bg-indigo-50 border-indigo-100 text-indigo-700",
        red: "bg-red-50 border-red-100 text-red-700",
        emerald: "bg-emerald-50 border-emerald-100 text-emerald-700",
        amber: "bg-amber-50 border-amber-100 text-amber-700",
    };
    return (
        <GlassCard className={cn("p-5 border-none shadow-sm flex items-center gap-4", colors[color])}>
            <div className="w-12 h-12 bg-white/80 rounded-2xl flex items-center justify-center shadow-sm">
                {icon}
            </div>
            <div>
                <p className="text-[10px] font-bold uppercase tracking-wider opacity-70">{label}</p>
                <p className="text-xl font-black">{value}</p>
            </div>
        </GlassCard>
    );
}

function getActionColor(action: string) {
    if (action.includes("CREATE") || action.includes("REGISTER")) return "bg-success-100 text-success-700";
    if (action.includes("DELETE") || action.includes("FAIL")) return "bg-red-100 text-red-700";
    if (action.includes("UPDATE")) return "bg-blue-100 text-blue-700";
    if (action.includes("LOGIN")) return "bg-amber-100 text-amber-700";
    return "bg-neutral-100 text-neutral-700";
}
