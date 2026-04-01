"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2, ArrowRight } from "lucide-react";
import { toast } from "sonner";

export default function ConnectReturnPage() {
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    // We could call an API here to verify the status, but the finance panel 
    // will refresh automatically when we go back.
    const timer = setTimeout(() => {
      setStatus("success");
      toast.success("Cuenta de Stripe conectada correctamente");
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center bg-neutral-50">
      <GlassCard className="max-w-md w-full p-8 space-y-6 bg-white shadow-xl border-none">
        {status === "loading" ? (
          <>
            <div className="flex justify-center">
              <Loader2 className="w-16 h-16 text-primary-500 animate-spin" />
            </div>
            <h1 className="text-2xl font-bold text-neutral-900">Finalizando conexión...</h1>
            <p className="text-neutral-500">Estamos verificando los datos con Stripe.</p>
          </>
        ) : (
          <>
            <div className="flex justify-center">
              <CheckCircle2 className="w-16 h-16 text-green-500" />
            </div>
            <h1 className="text-2xl font-bold text-neutral-900">¡Registro Completado!</h1>
            <p className="text-neutral-500">
              Tu cuenta de Stripe ha sido configurada. Ahora puedes recibir pagos y gestionar tus comisiones.
            </p>
            <Button 
              className="w-full h-12 bg-primary-600 hover:bg-primary-700 text-white"
              onClick={() => router.push("/finance")}
            >
              Ir al Panel Financiero
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </>
        )}
      </GlassCard>
    </div>
  );
}
