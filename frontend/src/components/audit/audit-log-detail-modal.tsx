"use client";

import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Terminal, 
  User, 
  Database, 
  Globe, 
  Clock, 
  Fingerprint,
  FileJson
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AuditLogDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  log: any;
}

export function AuditLogDetailModal({ isOpen, onClose, log }: AuditLogDetailModalProps) {
  if (!log) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl bg-white border-none shadow-2xl rounded-3xl overflow-hidden p-0">
        <div className="bg-neutral-900 p-6 text-white flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-white/10 flex items-center justify-center backdrop-blur-md border border-white/20">
              <Terminal className="w-6 h-6" />
            </div>
            <div>
              <DialogTitle className="text-xl font-bold">Detalle del Evento</DialogTitle>
              <DialogDescription className="text-neutral-400 text-xs font-mono">
                ID: {log.id}
              </DialogDescription>
            </div>
          </div>
          <Badge className={cn("font-mono px-3 py-1 border-none", getActionColor(log.action))}>
            {log.action}
          </Badge>
        </div>

        <div className="p-8 space-y-8">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <MetaItem icon={<User className="w-4 h-4" />} label="Agente" value={log.user_id?.split('-')[0] || "System"} />
            <MetaItem icon={<Database className="w-4 h-4" />} label="Entidad" value={log.entity} />
            <MetaItem icon={<Globe className="w-4 h-4" />} label="IP Address" value={log.ip_address || "127.0.0.1"} />
            <MetaItem icon={<Clock className="w-4 h-4" />} label="Timestamp" value={new Date(log.created_at).toLocaleTimeString()} />
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2 text-neutral-900 font-bold text-sm">
                <FileJson className="w-4 h-4 text-primary-500" />
                Detección Forense (Payload)
            </div>
            <ScrollArea className="h-[300px] w-full rounded-2xl border border-neutral-100 bg-neutral-50 p-6">
              <pre className="text-xs font-mono text-neutral-800 leading-relaxed whitespace-pre-wrap">
                {JSON.stringify(log.details || { info: "No se capturaron detalles adicionales para este evento." }, null, 2)}
              </pre>
            </ScrollArea>
          </div>

          <div className="flex items-center gap-2 p-4 bg-primary-50 rounded-2xl border border-primary-100">
             <Fingerprint className="w-5 h-5 text-primary-600" />
             <p className="text-[10px] text-primary-800 font-medium leading-tight">
                Este registro está firmado digitalmente y es inmutable. Cualquier alteración a la base de datos de auditoría disparará una alerta crítica al CSO.
             </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function MetaItem({ icon, label, value }: { icon: any, label: string, value: string }) {
    return (
        <div className="space-y-1.5">
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-neutral-400 uppercase tracking-widest">
                {icon}
                {label}
            </div>
            <div className="text-sm font-bold text-neutral-900 truncate">
                {value}
            </div>
        </div>
    )
}

function getActionColor(action: string) {
    if (action.includes("CREATE") || action.includes("REGISTER")) return "bg-success-500 text-white";
    if (action.includes("DELETE") || action.includes("FAIL")) return "bg-red-500 text-white";
    if (action.includes("UPDATE")) return "bg-blue-500 text-white";
    if (action.includes("LOGIN")) return "bg-amber-500 text-white";
    return "bg-neutral-500 text-white";
}
