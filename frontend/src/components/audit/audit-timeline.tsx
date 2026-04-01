"use client";

import { useQuery } from "@tanstack/react-query";
import { auditApi, AuditLog } from "@/lib/api/audit";
import { Skeleton } from "@/components/ui/skeleton";
import { History, User, Clock, AlertCircle } from "lucide-react";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import { Badge } from "@/components/ui/badge";

interface AuditTimelineProps {
  entityId: string;
  entityType?: string;
}

export function AuditTimeline({ entityId, entityType = "Company" }: AuditTimelineProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["audit-logs", entityType, entityId],
    queryFn: () => auditApi.getLogs({ entity: entityType, entity_id: entityId, page_size: 15 }),
  });

  if (isLoading) {
    return (
      <div className="space-y-8 pl-4 border-l-2 border-neutral-100 py-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="relative">
            <div className="absolute -left-7 top-1 w-4 h-4 rounded-full bg-neutral-200 border-4 border-white shadow-sm" />
            <Skeleton className="h-20 w-full rounded-2xl" />
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center text-error bg-red-50/50 rounded-2xl border border-red-100">
        <AlertCircle className="w-10 h-10 mb-4" />
        <h3 className="text-lg font-bold">Error al cargar el historial</h3>
        <p className="text-sm opacity-80 max-w-sm">No pudimos conectar con el motor de auditoría para obtener los registros detallados.</p>
      </div>
    );
  }

  if (!data?.items || data.items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-20 text-center text-neutral-400 bg-neutral-50/50 rounded-2xl border border-dashed border-neutral-200">
        <History className="w-16 h-16 mb-4 opacity-10" />
        <h3 className="text-lg font-bold text-neutral-900">Historial vacío</h3>
        <p className="text-sm max-w-sm">Aún no se han registrado acciones u operaciones para esta entidad en el sistema de trazabilidad.</p>
      </div>
    );
  }

  return (
    <div className="relative space-y-12 pl-8 border-l-2 border-primary-100/50 py-4">
      {data.items.map((log: AuditLog) => (
        <div key={log.id} className="relative animate-in slide-in-from-left-4 duration-500">
          {/* Timeline Dot */}
          <div className="absolute -left-10 top-0 w-5 h-5 rounded-full bg-white border-4 border-primary-500 shadow-md ring-8 ring-primary-50/30" />
          
          <div className="flex flex-col gap-3">
             <div className="flex items-center gap-3">
                <span className="text-xs font-mono font-bold text-primary-600 bg-primary-50 px-2 py-0.5 rounded-md uppercase tracking-wide">
                    {typeof log.action === 'string' ? log.action.replace(/_/g, " ") : "ACCIÓN"}
                </span>
                <span className="text-xs text-neutral-400 font-medium flex items-center gap-1.5">
                    <Clock className="w-3 h-3" />
                    {format(new Date(log.created_at), "PPP p", { locale: es })}
                </span>
             </div>

             <div className="flex items-start gap-4 p-5 rounded-2xl bg-white border border-neutral-100 hover:border-primary-200 hover:shadow-lg hover:shadow-primary-500/5 transition-all duration-300">
                <div className="w-10 h-10 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-500 shadow-inner">
                    <User className="w-5 h-5" />
                </div>
                <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                        <p className="text-sm font-bold text-neutral-900">
                            {typeof log.user_name === 'string' ? log.user_name : "Agente del Sistema"}
                        </p>
                        <Badge variant="outline" className="text-[10px] uppercase font-mono border-neutral-200 bg-neutral-50 text-neutral-500">
                            {typeof log.entity === 'string' ? log.entity : "Entidad"}
                        </Badge>
                    </div>
                    
                    {log.details && (
                        <div className="bg-neutral-50 rounded-xl p-3 border border-neutral-100">
                           <pre className="text-[10px] text-neutral-600 font-mono whitespace-pre-wrap leading-relaxed">
                            {JSON.stringify(log.details, null, 2)}
                           </pre>
                        </div>
                    )}
                </div>
             </div>
          </div>
        </div>
      ))}
    </div>
  );
}
