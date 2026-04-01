"use client";

import { useRouter } from "next/navigation";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { RefreshCw, AlertCircle } from "lucide-react";
import { toast } from "sonner";

export default function ConnectRefreshPage() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center bg-neutral-50">
      <GlassCard className="max-w-md w-full p-8 space-y-6 bg-white shadow-xl border-none">
        <div className="flex justify-center">
          <AlertCircle className="w-16 h-16 text-amber-500" />
        </div>
        <h1 className="text-2xl font-bold text-neutral-900">Sesión Expirada</h1>
        <p className="text-neutral-500">
          El proceso de registro de Stripe ha expirado por seguridad o has recargado la página manualmente.
        </p>
        <div className="space-y-3 pt-4">
          <Button 
            className="w-full h-12 bg-primary-600 hover:bg-primary-700 text-white"
            onClick={() => {
              toast.info("Reiniciando registro...");
              router.push("/finance");
            }}
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Reiniciar Registro
          </Button>
          <Button 
            variant="ghost"
            className="w-full text-neutral-500 hover:text-neutral-700"
            onClick={() => router.push("/finance")}
          >
            Volver al Panel
          </Button>
        </div>
      </GlassCard>
    </div>
  );
}
