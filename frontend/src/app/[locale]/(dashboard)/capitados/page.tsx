"use client";

import { useTranslations } from "next-intl";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Upload, Users, Info, FileText } from "lucide-react";
import { Link } from "@/navigation";
import { useQuery } from "@tanstack/react-query";
import { capitadosApi } from "@/lib/api/modules";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

export default function CapitadosPage() {
  const t = useTranslations("dashboard");

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--color-neutral-900)] tracking-tight">
            Capitados
          </h1>
          <p className="text-[var(--color-neutral-500)] mt-1">
            Gestión masiva de asegurados mediante archivos de carga
          </p>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" className="border-[var(--color-primary-500)] text-[var(--color-primary-600)] hover:bg-primary-50">
            <FileText className="w-5 h-5 mr-2" />
            Descargar Plantilla
          </Button>
          <Button className="bg-[var(--color-primary-500)] hover:bg-[var(--color-primary-600)] text-white shadow-lg shadow-primary-500/20">
            <Upload className="w-5 h-5 mr-2" />
            Cargar Lote
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <GlassCard className="lg:col-span-1 p-6 space-y-4 h-fit border-none shadow-glass">
          <h3 className="text-lg font-bold text-neutral-900 border-b pb-4">
            Resumen Operativo
          </h3>
          <div className="space-y-6 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-500">Capitados Activos</span>
              <span className="text-xl font-bold text-primary-600">8,920</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-neutral-500">Lotes Procesados</span>
              <span className="text-xl font-bold text-info">24</span>
            </div>
          </div>
          <div className="pt-6 border-t border-neutral-100 flex items-center justify-start gap-2 text-warning">
            <Info className="w-4 h-4" />
            <span className="text-xs font-medium">Hay 2 lotes en revisión manual.</span>
          </div>
        </GlassCard>

        <GlassCard className="lg:col-span-2 p-6 flex flex-col h-[500px] border-none shadow-glass">
           <h3 className="text-lg font-bold text-neutral-900 mb-6">
            Historial de Cargas Recientes
          </h3>
          <div className="flex-1 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center mb-4">
              <Users className="w-8 h-8 text-neutral-300" />
            </div>
            <h3 className="text-xl font-bold text-neutral-900">Sin cargas recientes</h3>
            <p className="text-neutral-500 max-w-sm mt-2">
              Sube un archivo Excel para ver el listado de capitados y su estado de procesamiento.
            </p>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
