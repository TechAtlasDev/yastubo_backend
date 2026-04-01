"use client";

import React, { useState } from "react";
import {
  useStripe,
  useElements,
  PaymentElement,
  Elements,
} from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import { Button } from "@/components/ui/button";
import { financeApi } from "@/lib/api/modules";
import { toast } from "sonner";
import { Loader2, ShieldCheck, CreditCard } from "lucide-react";

// In production, this should be an environment variable
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "pk_test_sample");

interface PaymentGatewayProps {
  policyId: string;
  onSuccess?: () => void;
  onCancel?: () => void;
  amount?: string;
}

export function PaymentGateway({ policyId, onSuccess, onCancel, amount }: PaymentGatewayProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  const startPayment = async () => {
    setIsProcessing(true);
    try {
      const response = await financeApi.createPaymentIntent({ policy_id: policyId });
      if (response.client_secret) {
        setClientSecret(response.client_secret);
        toast.success("Pasarela preparada. Complete el pago.");
      } else {
        toast.error("No se pudo obtener el secreto del cliente.");
      }
    } catch (error) {
      console.error("Payment Intent Error:", error);
      toast.error("Error al iniciar el pago.");
    } finally {
      setIsProcessing(false);
    }
  };

  if (!clientSecret) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white rounded-xl border border-dashed border-neutral-300 gap-4 text-center">
        <CreditCard className="w-12 h-12 text-blue-500 mb-2" />
        <div>
          <h3 className="text-lg font-semibold">Pagar Póliza</h3>
          <p className="text-sm text-neutral-500">
            Haga clic abajo para iniciar el proceso de pago seguro para la póliza seleccionada.
          </p>
        </div>
        <Button onClick={startPayment} disabled={isProcessing} className="w-full max-w-xs">
          {isProcessing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
          {isProcessing ? "Procesando..." : "Preparar Pago Seguro"}
        </Button>
      </div>
    );
  }

  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <PaymentForm
        isProcessing={isProcessing}
        setIsProcessing={setIsProcessing}
        onSuccess={onSuccess}
        onCancel={onCancel}
        amount={amount}
      />
    </Elements>
  );
}

function PaymentForm({
  isProcessing,
  setIsProcessing,
  onSuccess,
  onCancel,
  amount,
}: {
  isProcessing: boolean;
  setIsProcessing: (val: boolean) => void;
  onSuccess?: () => void;
  onCancel?: () => void;
  amount?: string;
}) {
  const stripe = useStripe();
  const elements = useElements();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) return;

    setIsProcessing(true);

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/finance/success`,
      },
      redirect: "if_required",
    });

    if (error) {
      toast.error(error.message || "Error en el pago");
    } else if (paymentIntent && paymentIntent.status === "succeeded") {
      toast.success("Pago completado con éxito");
      onSuccess?.();
    }

    setIsProcessing(false);
  };

  return (
    <div className="bg-white p-6 rounded-xl border shadow-sm">
      <div className="flex items-center gap-2 mb-6 text-green-600">
        <ShieldCheck className="w-5 h-5" />
        <span className="text-sm font-medium">Pago Seguro Encriptado (Stripe)</span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <PaymentElement />
        <div className="flex gap-3 pt-4">
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={onCancel}
              disabled={isProcessing}
            >
              Cancelar
            </Button>
          )}
          <Button
            type="submit"
            className="flex-1"
            disabled={!stripe || isProcessing}
          >
            {isProcessing ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : null}
            {isProcessing ? "Confirmando..." : `Pagar Ahora ${amount ? amount : ""}`}
          </Button>
        </div>
      </form>
    </div>
  );
}

